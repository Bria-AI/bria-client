import json
import os
import urllib.parse
from datetime import datetime
from typing import Dict, List
from uuid import uuid4

import firebase_admin
from core.secrets import SecretId, Secrets
from firebase_admin import auth, credentials, db

from bria_internal.common.singleton_meta import SingletonABCMeta
from bria_internal.firebase.constants import ORGS_DB_NAME, USERS_DB_NAME, USERS_INVITATION_DB_NAME
from bria_internal.firebase.enums import (
    ApiKeyStatus,
    ApiSubscriptionStatuses,
    ApiSubscriptionTypes,
    InvitationStatus,
    OrgUserRoles,
    OrgUserStatus,
    SubscriptionPeriods,
    UserRoles,
    VDRImageState,
)
from bria_internal.firebase.models import ApiSubscription, AuthUser, Invitation, Organization, User, UserOrganization


class Firebase(metaclass=SingletonABCMeta):
    SERVICE_AVAILABILITY_THRESHOLD = 60

    def __init__(self):
        self.web_subscription_config_cache = {}
        self.token_cache = {}
        self.org_cache = {}
        if not firebase_admin._apps:
            service_account_key_path = "/tmp/service_account_key.json"
            if not os.path.exists(service_account_key_path):
                FIREBASE_SERVICE_ACCOUNT_KEY = Secrets().get_secret_for(id=SecretId.FIREBASE_SERVICE_ACCOUNT_KEY)
                service_account_key = json.loads(FIREBASE_SERVICE_ACCOUNT_KEY)
                with open(service_account_key_path, "w") as outfile:
                    json.dump(service_account_key, outfile)
            cred = credentials.Certificate(service_account_key_path)
            self.app = firebase_admin.initialize_app(
                cred,
                {"databaseURL": "https://image-viewer-120cb.firebaseio.com/"},
            )

    def verify_id_token(self, id_token: str) -> AuthUser:
        decoded_token = auth.verify_id_token(id_token=id_token)
        return AuthUser(user_id=decoded_token["user_id"], role=decoded_token["role"])

    def get_organization_by_api_token(self, api_token: str) -> dict:
        selected_org = None
        orgs = db.reference(f"{ORGS_DB_NAME}").get().values()
        for org in orgs:
            for key in org["api_keys"]:
                if key["api_token"] == api_token and key["status"] == "active":
                    selected_org = org
        return selected_org

    def api_authorization_with(self, api_token: str) -> dict:
        org = self.get_organization_by_api_token(api_token)
        if org is None:
            raise Exception("Invalid customer token key")
        return org

    def update_user_info(self, user_id: str, new_profile_picture_url: str, user_name: str, userRole: str, user_company: str = None):
        user_ref = db.reference(f"users/{user_id}")
        user_ref.update({"profile_picture": new_profile_picture_url, "user_name": user_name, "userRole": userRole, "company": user_company})
        return True

    def is_user_permitted_to_organization(self, firebase_user: dict, org_id: str, allowed_org_user_roles: List[OrgUserRoles]) -> bool:
        user_role = firebase_user.get("role", UserRoles.VIEWER.value).lower()
        user_uid = firebase_user.get("uid")
        if user_role == UserRoles.ADMIN.value:
            # user role is super admin
            return True

        # check if org is a parent org and user has direct access to ot
        user_organizations_list = []
        try:
            user_organizations_list = self.__get_user_organizations(user_uid, ignore_implicit_organizations=False)
        except Exception as exp:
            if "User is not part of an any organization" not in exp.args:
                raise exp
        user_organization = None
        for user_org in user_organizations_list:
            if user_org.org_uid == org_id:
                user_organization = user_org

        if user_organization is not None:
            # target org is a parent org, user has direct role
            if OrgUserRoles(user_organization.role) in allowed_org_user_roles:
                return True
        else:
            # target org is a child org, user is only permitted if org admin/owner
            user_child_organizations = self.list_user_organizations(
                user_uid=user_uid, fetch_child_organizations=True, user_organizations_list=user_organizations_list
            )
            for child_organization in user_child_organizations:
                if org_id == child_organization.org_uid:
                    return True
        # selected organization is neither a parent nor child, or user doesn't have the required role
        return False

    def get_organizations(self, user_uid: str, fetch_child_organizations: bool = False) -> List[Organization]:
        user_organizations = self.list_user_organizations(user_uid, fetch_child_organizations)
        organizations_list = [user_org.organization for user_org in user_organizations]
        return organizations_list

    def get_child_organizations(self, org):
        result = []
        firebase = Firebase()
        if org.child_organizations is None:
            return result
        for user_child_org in org.child_organizations:
            organization_obj = firebase.get_organization(user_child_org["uid"])
            result.append(organization_obj)
        return result

    def list_user_organizations(
        self,
        user_uid: str,
        fetch_child_organizations: bool = False,
        ignore_implicit_organizations: bool = True,
        user_organizations_list: List[UserOrganization] = None,
    ) -> List[UserOrganization]:
        organizations_list = []

        # ignore organizations with implicit relationship to avoid redundancy in OrgDropdown
        try:
            user_organizations_list = (
                self.__get_user_organizations(user_uid, ignore_implicit_organizations=ignore_implicit_organizations)
                if user_organizations_list is None
                else user_organizations_list
            )
        except Exception as exp:
            user_organizations_list = []
            if "User is not part of an any organization" not in exp.args:
                raise exp
        for user_organization in user_organizations_list:
            organization = self.get_organization(user_organization.org_uid)
            user_organization.organization = organization
            organizations_list.append(user_organization)
            if fetch_child_organizations and user_organization.role.lower() in [OrgUserRoles.ADMIN.value, OrgUserRoles.OWNER.value]:
                child_organizations = [
                    UserOrganization(
                        org_uid=child_org.uid,
                        role=OrgUserRoles.ADMIN.value,
                        organization=child_org,
                    )
                    for child_org in self.get_child_organizations(organization)
                ]
                organizations_list = organizations_list + child_organizations

        return organizations_list

    def update_user_organization_field(self, user_id: str, new_value: str, org_id: str, field: str = "role") -> User:
        def change_field_transaction(user_organizations):
            is_updated = False
            for org in user_organizations:
                if org.get("org_uid") == org_id:
                    org[field] = new_value
                    is_updated = True
                    break
            if not is_updated:
                self.add_user_to_organization(user_id, org_id)
                user_organizations = db.reference(f"{USERS_DB_NAME}/{user_id}/user_organizations").get()
                for org in user_organizations:
                    if org.get("org_uid") == org_id:
                        org[field] = new_value
                        break
            return user_organizations

        ref = db.reference(f"{USERS_DB_NAME}/{user_id}/user_organizations")
        ref.transaction(change_field_transaction)
        updated_user_data = db.reference(f"{USERS_DB_NAME}/{user_id}").get()
        return User(**updated_user_data)

    def delete_user_organization(self, user_id, org_id):
        def change_field_transaction(user_organizations):
            updated_user_organizations = user_organizations.copy()

            for org in user_organizations:
                if org.get("org_uid") == org_id:
                    updated_user_organizations.remove(org)
                    break

            return updated_user_organizations

        ref = db.reference(f"{USERS_DB_NAME}/{user_id}/user_organizations")
        ref.transaction(change_field_transaction)
        updated_user_data = db.reference(f"{USERS_DB_NAME}/{user_id}").get()

        return User(**updated_user_data)

    def __get_user_organizations(self, user_uid: str, ignore_implicit_organizations: bool = False) -> List[UserOrganization]:
        ref = db.reference(USERS_DB_NAME)
        organizations = ref.child(f"{user_uid}/user_organizations").get()
        if organizations is None:
            raise Exception("User is not part of an any organization")
        organizations = [
            UserOrganization(org_uid=org["org_uid"], role=org["role"], status=org.get("status", None))
            for org in organizations
            if org["org_uid"] != "6f9007a7-cfd4-49b2-bf4b-be3a11e869a7"
            and org.get("status", None) != OrgUserStatus.DELETED.value
            and (not ignore_implicit_organizations or (org.get("role", None) not in [OrgUserRoles.ADMIN_HIDDEN.value, OrgUserRoles.USER_HIDDEN.value]))
        ]
        return organizations

    def get_customer_auth_data(self, customer_token: str) -> List[Organization]:
        if customer_token in self.org_cache:
            return self.org_cache[customer_token]
        token_attr = self.get_or_create_token_attr(api_token=customer_token)
        org_uid = token_attr.get("uid")
        org_ref = db.reference(f"{ORGS_DB_NAME}/{org_uid}")
        customer_auth_data = org_ref.child("customer_auth_data").get() or {}

        # Cache the result before returning
        self.org_cache[customer_token] = customer_auth_data
        return customer_auth_data

    def get_organization_users(self, org_uid: str, allowed_user_roles=None) -> List[User]:
        users = db.reference(USERS_DB_NAME).get()

        def is_in_organization(user: Dict):
            orgs = user.get("user_organizations")
            if orgs is None:
                return None
            for org in orgs:
                if org.get("org_uid") == org_uid:
                    if allowed_user_roles and org.get("role") not in allowed_user_roles:
                        continue
                    return user
            return None

        result = sorted([user for user in users.values() if is_in_organization(user)], key=lambda user: user["user_name"])
        return [User(**user) for user in result]

    def get_user(self, user_uid: str):
        ref = db.reference(f"{USERS_DB_NAME}/{user_uid}")
        return User(**ref.get())

    def get_all_users(self):
        ref = db.reference(USERS_DB_NAME).get()
        values = ref.values()
        for user in values:
            if "settings" in user:
                del user["settings"]
        return [User(**user) for user in values]

    def delete_user(self, user_uid: str):
        # Delete user from RealTime firebase
        ref = db.reference(f"{USERS_DB_NAME}/{user_uid}")
        ref.delete()

        # Delete user from firebase authentication
        self.delete_user_by_id(user_uid)
        return True

    # Classification
    def set_vdr_image_state(self, visual_hash: str, state: VDRImageState):
        ref = db.reference("vdr_images_info")
        ref.child(visual_hash).set({"state": state.value})

    def set_custom_user_role(self, uid: str, role: str):
        auth.set_custom_user_claims(uid, {"role": role})

    def delete_user_by_id(self, uid: str):
        auth.delete_user(uid)

    def set_user_email_verification_flag(self, uid: str, verified: bool):
        auth.update_user(uid, email_verified=verified)

    def decode_id_token(self, id_token: str):
        return auth.verify_id_token(id_token=id_token)

    def search_organizations(self, query: str, limit: int = 0):
        if query is None:
            return []
        ref = db.reference(ORGS_DB_NAME).order_by_child("name").start_at(urllib.parse.quote(query.lower()))
        if limit > 0:
            ref = ref.limit_to_first(limit)
        values = ref.get().values()
        return [Organization(**organization) for organization in values]

    def get_all_organizations(self, limit: int = 0):
        ref = db.reference(ORGS_DB_NAME).order_by_child("name")
        if limit > 0:
            ref = ref.limit_to_first(limit)
        values = ref.get().values()
        return [Organization(**organization) for organization in values]

    def add_user_to_organization(self, user_uid: str, organization_id: str, role: str = OrgUserRoles.USER.value):
        try:
            new_org_json = UserOrganization(org_uid=organization_id, role=role, status=OrgUserStatus.ACTIVE.value).to_json()
            ref = db.reference(f"{USERS_DB_NAME}/{user_uid}")
            user_organizations = ref.child("user_organizations").get()
            if user_organizations is None:
                user_organizations = [new_org_json]
            else:
                already_exists = any(org["org_uid"] == organization_id for org in user_organizations)
                if not already_exists:
                    user_organizations.append(new_org_json)
            ref.child("user_organizations").set(user_organizations)
        except Exception as error:
            raise error

    def post_user_invitation(self, invitation):
        try:
            ref = db.reference(f"{USERS_INVITATION_DB_NAME}/{invitation['token']}")
            ref.set(invitation)
        except Exception as error:
            raise error

    def get_user_invitation(self, token):
        try:
            ref = db.reference(f"{USERS_INVITATION_DB_NAME}/{token}")
            invitation_obj = ref.get()
            if invitation_obj and invitation_obj.get("status") == InvitationStatus.ACTIVE.value:
                return Invitation(**invitation_obj)
            else:
                return None
        except Exception as error:
            raise error

    def update_invitation_field(self, token, new_value, field="status"):
        def change_field_transaction(invitation):
            invitation[field] = new_value
            return invitation

        ref = db.reference(f"{USERS_INVITATION_DB_NAME}/{token}")
        invitation = ref.transaction(change_field_transaction)
        return Invitation(**invitation)

    def get_user_by_id(self, user_id):
        ref = db.reference(f"{USERS_DB_NAME}/{user_id}")
        return ref.get()

    def get_user_ref_by_id(self, user_id):
        ref = db.reference(f"{USERS_DB_NAME}/{user_id}")
        return ref

    def get_user_galleries_ids(self, user_id: str, role: str):
        galleries_ids = []
        user = self.get_user_by_id(user_id)
        if user and "gallery_permissions" in user and role in user["gallery_permissions"]:
            galleries_ids = user["gallery_permissions"][role]
        return galleries_ids

    def add_asset_to_user(self, user_uid, asset_id, access_levels: List[str]):
        def persmission_transaction(user):
            if "gallery_permissions" not in user:
                user["gallery_permissions"] = {}
            for access_level in access_levels:
                if access_level not in user["gallery_permissions"]:
                    user["gallery_permissions"][access_level] = []
                user_permissions = set(user["gallery_permissions"][access_level])
                user_permissions.add(asset_id)
                user["gallery_permissions"][access_level] = list(user_permissions)
            return user

        try:
            ref = db.reference(f"{USERS_DB_NAME}/{user_uid}")
            ref.transaction(persmission_transaction)
        except Exception as error:
            raise error

    def get_organization_by_id(self, org_id):
        ref = db.reference(f"{ORGS_DB_NAME}/{org_id}")
        return ref.get()

    def get_organization(self, org_id):
        ref = db.reference(f"{ORGS_DB_NAME}/{org_id}")
        return Organization(**ref.get())

    def get_org_by_name(self, name: str):
        org = None
        try:
            orgs = list(db.reference(f"{ORGS_DB_NAME}").order_by_child("name").equal_to(urllib.parse.quote(name.lower())).get().values())
            if len(orgs) > 0:
                org = orgs[0]
        except Exception as error:
            raise error
        return org

    def get_or_create_token_attr(self, api_token):
        if api_token in self.token_cache:
            return self.token_cache[api_token]
        ref = db.reference(f"token_attributes/{api_token}")
        token_attr = ref.get()
        if not token_attr or "key_type" not in token_attr:
            org = self.api_authorization_with(api_token)
            if org:
                key_type = None
                for key in org["api_keys"]:
                    if key["api_token"] == api_token:
                        key_type = key["key_type"]
                        break
                assert key_type is not None, "key type is None"
                token_attr = {"name": org.get("name"), "uid": org.get("uid"), "key_type": key_type}
                ref.set(token_attr)
            else:
                raise Exception("Invalid customer token key")

        # Cache the result before returning
        self.token_cache[api_token] = token_attr
        return token_attr

    def update_organization_owner(self, org_uid: str, new_owner_uid: str):
        org_ref = db.reference(f"{ORGS_DB_NAME}/{org_uid}")
        org_snapshot = org_ref.get()
        if org_snapshot:
            org_snapshot["owner_uid"] = new_owner_uid
            org_ref.set(org_snapshot)
            return True
        else:
            return False

    def create_organization(
        self,
        org_name: str,
        owner_uid: str,
        plan: ApiSubscriptionTypes = ApiSubscriptionTypes.STARTER,
        api_subscription_status: ApiSubscriptionStatuses = ApiSubscriptionStatuses.ACTIVE,
        api_subscription_period: SubscriptionPeriods = SubscriptionPeriods.DEFAULT,
        start_date: datetime = datetime.now(),
        uid: str | None = None,
        default_api_key_status: ApiKeyStatus = ApiKeyStatus.INACTIVE,
    ):
        org_uid = uid or str(uuid4())
        ref = db.reference(f"{ORGS_DB_NAME}/{org_uid}")
        (
            iframe_api_key,
            internal_api_key,
            api_key,
            staging_api_key,
            comfyui_api_key,
            mcp_api_key,
        ) = Organization.create_initial_org_api_keys(api_subscription_status=api_subscription_status, default_api_key_status=default_api_key_status)
        org_name = org_name.lower()
        ref.set(
            {
                "uid": org_uid,
                "owner_uid": owner_uid,
                "name": org_name,
                "api_keys": [
                    iframe_api_key.to_json(),
                    internal_api_key.to_json(),
                    api_key.to_json(),
                    staging_api_key.to_json(),
                    comfyui_api_key.to_json(),
                    mcp_api_key.to_json(),
                ],
                "api_token": api_key.api_token,
                "logo_url": "",
                "api_subscription": ApiSubscription.get_default_api_subscription(
                    api_subscription_type=plan,
                    start_date=start_date,
                    api_subscription_period=api_subscription_period,
                    api_subscription_status=api_subscription_status,
                ).to_json(),
            }
        )
        return org_uid, api_key.api_token
