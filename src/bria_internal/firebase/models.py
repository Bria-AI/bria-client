from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import uuid4

import graphene
from firebase_admin import db

from bria_internal.firebase.enums import (
    ApiKeyStatus,
    ApiKeyTypes,
    ApiSubscriptionStatuses,
    ApiSubscriptionTypes,
    SubscriptionPeriods,
    SubscriptionTypes,
)


class DynamicObjectType(graphene.ObjectType):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except TypeError as type_error:
            if "invalid keyword argument" in str(type_error):
                print(f"WARNING: {type_error}")
            else:
                raise type_error


class CustomerClientSecret(DynamicObjectType):
    customer_client_secret = graphene.String(required=False)
    customer_client_id = graphene.String(required=False)
    customer_access_type = graphene.String(required=False)
    customer_url = graphene.String(required=False)


class ApiSubscriptionConfig(DynamicObjectType):
    name = graphene.NonNull(graphene.String)
    display_name = graphene.NonNull(graphene.String)
    product_id = graphene.NonNull(graphene.String)
    store_id = graphene.NonNull(graphene.String)
    contract_yearly_id = graphene.NonNull(graphene.String)
    contract_monthly_id = graphene.NonNull(graphene.String)
    monthly_price = graphene.NonNull(graphene.Float)
    yearly_monthly_price = graphene.NonNull(graphene.Float)
    api_call_price = graphene.NonNull(graphene.Float)
    monthly_included_calls = graphene.NonNull(graphene.Int)
    free_calls_routes = graphene.NonNull(graphene.List(graphene.NonNull(graphene.String)))
    iframe = graphene.NonNull(graphene.Int)
    white_labeled_iframe = graphene.NonNull(graphene.Int)
    search_discount = graphene.NonNull(graphene.Float)
    integration_support = graphene.NonNull(graphene.Int)


class ApiSubscription(DynamicObjectType):
    bs_api_subscription_id = graphene.NonNull(graphene.String)
    bs_api_shopper_id = graphene.NonNull(graphene.String)
    api_subscription_period = graphene.NonNull(graphene.String)
    api_subscription_start_date = graphene.NonNull(graphene.String)
    api_subscription_status = graphene.NonNull(graphene.String)
    api_subscription_type = graphene.NonNull(graphene.String)

    @staticmethod
    def get_default_api_subscription(
        api_subscription_type: ApiSubscriptionTypes,
        start_date: datetime,
        api_subscription_period: SubscriptionPeriods = SubscriptionPeriods.DEFAULT,
        api_subscription_status: ApiSubscriptionStatuses = ApiSubscriptionStatuses.NOT_ACTIVE,
    ):
        start_date_formatted = ApiSubscription.format_subscription_date(start_date)
        api_subscription = ApiSubscription(
            bs_api_subscription_id="",
            bs_api_shopper_id="",
            api_subscription_period=api_subscription_period.value,
            api_subscription_start_date=start_date_formatted,
            api_subscription_status=api_subscription_status.value,
            api_subscription_type=api_subscription_type.value,
        )
        return api_subscription

    def to_json(self):
        return {
            "bs_api_subscription_id": self.bs_api_subscription_id,
            "bs_api_shopper_id": self.bs_api_shopper_id,
            "api_subscription_period": self.api_subscription_period,
            "api_subscription_start_date": self.api_subscription_start_date,
            "api_subscription_status": self.api_subscription_status,
            "api_subscription_type": self.api_subscription_type,
        }

    def get_subscription_type(self):
        return ApiSubscriptionTypes(self.api_subscription_type)

    @staticmethod
    def format_subscription_date(dt: datetime) -> str:
        return dt.strftime("%d/%m/%Y")


class TokenAttributes(DynamicObjectType):
    api_token = graphene.NonNull(graphene.String)
    uid = graphene.NonNull(graphene.String)
    name = graphene.NonNull(graphene.String)

    def to_json(self):
        return {
            "api_token": self.api_token,
            "uid": self.uid,
            "name": self.name,
        }


class ApiKey(DynamicObjectType):
    api_token = graphene.NonNull(graphene.String)
    status = graphene.NonNull(graphene.String)
    created = graphene.NonNull(graphene.String)
    key_type = graphene.NonNull(graphene.String)

    def to_json(self):
        return {
            "api_token": self.api_token,
            "status": self.status,
            "created": self.created,
            "key_type": self.key_type,
        }


class ChildOrganization(DynamicObjectType):
    uid = graphene.NonNull(graphene.String)

    def to_json(self):
        return {"uid": self.uid}


class Organization(DynamicObjectType):
    level = graphene.String(required=False)
    child_organizations = graphene.List(ChildOrganization, required=False)
    api_keys = graphene.List(ApiKey, required=False)
    api_token = graphene.String(required=False)
    uid = graphene.NonNull(graphene.String)
    plan = graphene.String()
    name = graphene.NonNull(graphene.String)
    logo_url = graphene.String(required=False)
    owner_uid = graphene.String(required=False)
    customer_auth_data = graphene.Field(CustomerClientSecret, required=False)
    api_subscription = graphene.Field(ApiSubscription, required=False)

    def to_json(self):
        return {
            "level": self.level,
            "api_keys": self.api_keys,
            "child_organizations": self.child_organizations,
            "api_token": self.api_token,
            "owner_uid": self.owner_uid,
            "uid": self.uid,
            "name": self.name,
            "logo_url": self.logo_url,
            "customer_auth_data": self.customer_auth_data,
            "api_subscription": self.api_subscription,
        }

    def create_missing_api_keys(self):
        existing_key_types = {key["key_type"] for key in self.api_keys}
        required_key_types = {
            ApiKeyTypes.PRODUCTION.value,
            ApiKeyTypes.STAGING.value,
            ApiKeyTypes.COMFY.value,
            ApiKeyTypes.MCP.value,
        }
        missing_key_types = required_key_types - existing_key_types
        newly_added_keys = []
        for key_type in missing_key_types:
            new_api_key = Organization.add_api_key(
                org_id=self.uid,
                key_type=ApiKeyTypes(key_type),
                status=ApiKeyStatus.ACTIVE,
            )
            newly_added_keys.append(new_api_key.to_json())
        self.api_keys += newly_added_keys

    def get_api_keys(self, include_internal=False):
        self.create_missing_api_keys()
        if include_internal:
            return self.api_keys
        internals_keys = [
            ApiKeyTypes.INTERNAL.value,
            ApiKeyTypes.IFRAME.value,
            ApiKeyTypes.FIGMA_PLUGIN.value,
            ApiKeyTypes.PHOTOSHOP_PLUGIN.value,
        ]
        return list(filter(lambda k: k["key_type"] not in internals_keys, self.api_keys))

    def get_api_keys_by_type(self, api_key_types: List[str]) -> List[ApiKey]:
        filtered_api_keys = [ApiKey(**k) for k in self.api_keys if k["key_type"] in api_key_types]
        return filtered_api_keys

    def get_or_create_api_key(self, api_key_type: ApiKeyTypes) -> ApiKey:
        api_keys = self.get_api_keys_by_type([api_key_type.value])
        api_key = api_keys[0] if api_keys else None
        return api_key or Organization.add_api_key(org_id=self.uid, key_type=api_key_type, status=ApiKeyStatus.ACTIVE)

    def get_internal_api_key(self) -> ApiKey:
        return self.get_or_create_api_key(ApiKeyTypes.INTERNAL)

    def get_iframe_api_key(self) -> ApiKey:
        return self.get_or_create_api_key(ApiKeyTypes.IFRAME)

    def get_child_orgs_ids(self):
        if self.child_organizations is None:
            return []
        child_org_uids = [child_org.get("uid", "") for child_org in self.child_organizations]
        return child_org_uids

    @staticmethod
    def generate_api_key(key_type=ApiKeyTypes.INTERNAL, status=ApiKeyStatus.ACTIVE) -> "ApiKey":
        api_token = str(uuid4()).replace("-", "")
        created = date.today().strftime("%b %d, %Y")
        api_key = ApiKey(
            api_token=api_token,
            created=created,
            status=status.value,
            key_type=key_type.value,
        )
        return api_key

    @staticmethod
    def create_initial_org_api_keys(
        api_subscription_status: ApiSubscriptionStatuses = ApiSubscriptionStatuses.ACTIVE,
        default_api_key_status: ApiKeyStatus = ApiKeyStatus.INACTIVE,
    ):
        internal_api_key = Organization.generate_api_key(status=ApiKeyStatus.ACTIVE, key_type=ApiKeyTypes.INTERNAL)
        iframe_api_key = Organization.generate_api_key(status=ApiKeyStatus.ACTIVE, key_type=ApiKeyTypes.IFRAME)
        api_key = Organization.generate_api_key(
            status=default_api_key_status if api_subscription_status == ApiSubscriptionStatuses.NOT_ACTIVE else ApiKeyStatus.ACTIVE,
            key_type=ApiKeyTypes.PRODUCTION,
        )
        staging_api_key = Organization.generate_api_key(
            status=default_api_key_status if api_subscription_status == ApiSubscriptionStatuses.NOT_ACTIVE else ApiKeyStatus.ACTIVE,
            key_type=ApiKeyTypes.STAGING,
        )
        comfyui_api_key = Organization.generate_api_key(
            status=default_api_key_status if api_subscription_status == ApiSubscriptionStatuses.NOT_ACTIVE else ApiKeyStatus.ACTIVE,
            key_type=ApiKeyTypes.COMFY,
        )
        mcp_api_key = Organization.generate_api_key(
            status=default_api_key_status if api_subscription_status == ApiSubscriptionStatuses.NOT_ACTIVE else ApiKeyStatus.ACTIVE,
            key_type=ApiKeyTypes.MCP,
        )
        return (
            iframe_api_key,
            internal_api_key,
            api_key,
            staging_api_key,
            comfyui_api_key,
            mcp_api_key,
        )

    @staticmethod
    def add_api_key(
        org_id,
        key_type: ApiKeyTypes,
        status: ApiKeyStatus,
    ) -> "ApiKey":
        from bria_internal.firebase.constants import ORGS_DB_NAME

        api_key = Organization.generate_api_key(key_type=key_type, status=status)

        def api_key_transaction(org):
            if "api_keys" not in org:
                org["api_keys"] = []
            org["api_keys"].append(api_key.to_json())
            return org

        ref = db.reference(f"{ORGS_DB_NAME}/{org_id}")
        ref.transaction(api_key_transaction)
        return api_key

    @staticmethod
    def update_api_key(org_id, api_token, new_status) -> Optional["ApiKey"]:
        from bria_internal.firebase.constants import ORGS_DB_NAME

        def change_status_transaction(api_keys):
            for key in api_keys:
                if key.get("api_token") == api_token:
                    key["status"] = new_status
            return api_keys

        ref = db.reference(f"{ORGS_DB_NAME}/{org_id}/api_keys")
        api_keys = ref.transaction(change_status_transaction)

        result_api_key = None
        for key in api_keys:
            if key["api_token"] == api_token:
                result_api_key = ApiKey(**key)
                break

        return result_api_key

    @staticmethod
    def enable_api_key(api_key: Dict):
        if api_key is not None and api_key["status"] == ApiKeyStatus.INACTIVE.value:
            api_key["status"] = ApiKeyStatus.ACTIVE.value

    @staticmethod
    def disable_api_key(api_key: Dict):
        if api_key is not None and api_key["status"] == ApiKeyStatus.ACTIVE.value:
            api_key["status"] = ApiKeyStatus.INACTIVE.value


class GalleryPermissions(DynamicObjectType):
    read = graphene.List(graphene.NonNull(graphene.String), required=False)
    write = graphene.List(graphene.NonNull(graphene.String), required=False)


class SubscriptionConfig(DynamicObjectType):
    name = graphene.NonNull(graphene.String)
    display_name = graphene.NonNull(graphene.String)
    brands = graphene.NonNull(graphene.Int)
    download = graphene.NonNull(graphene.Int)
    download_psd = graphene.NonNull(graphene.Int)
    increase_resolution = graphene.NonNull(graphene.Int)
    illustration_generation = graphene.NonNull(graphene.String)
    my_assets = graphene.NonNull(graphene.Int)
    object_customizations = graphene.NonNull(graphene.Int)
    people_customizations = graphene.NonNull(graphene.Int)
    premium_stock_images = graphene.NonNull(graphene.Int)
    premium_support = graphene.NonNull(graphene.Int)
    remove_bg = graphene.NonNull(graphene.Int)
    search_my_assets = graphene.NonNull(graphene.Int)
    upload = graphene.NonNull(graphene.Int)
    videos = graphene.NonNull(graphene.Int)
    product_id = graphene.NonNull(graphene.String)
    store_id = graphene.NonNull(graphene.String)
    contract_yearly_id = graphene.NonNull(graphene.String)
    contract_monthly_id = graphene.NonNull(graphene.String)
    monthly_price = graphene.NonNull(graphene.Float)
    yearly_monthly_price = graphene.NonNull(graphene.Float)


class Subscription(DynamicObjectType):
    web_subscription_type = graphene.NonNull(graphene.String)
    web_subscription_start_date = graphene.NonNull(graphene.String)
    download_credits = graphene.NonNull(graphene.Int)
    download_psd_credits = graphene.NonNull(graphene.Int)
    videos_credits = graphene.NonNull(graphene.Int)
    people_customizations_credits = graphene.NonNull(graphene.Int)
    object_customizations_credits = graphene.NonNull(graphene.Int)
    bs_web_subscription_id = graphene.NonNull(graphene.String)
    bs_web_shopper_id = graphene.NonNull(graphene.String)
    web_subscription_period = graphene.NonNull(graphene.String)

    def to_json(self):
        return {
            "web_subscription_type": self.web_subscription_type,
            "web_subscription_start_date": self.web_subscription_start_date,
            "videos_credits": self.videos_credits,
            "download_credits": self.download_credits,
            "download_psd_credits": self.download_psd_credits,
            "people_customizations_credits": self.people_customizations_credits,
            "object_customizations_credits": self.object_customizations_credits,
            "bs_web_subscription_id": self.bs_web_subscription_id,
            "bs_web_shopper_id": self.bs_web_shopper_id,
            "web_subscription_period": self.web_subscription_period,
        }

    def get_subscription_type(self):
        return SubscriptionTypes(self.web_subscription_type)

    @staticmethod
    def format_subscription_date(dt: datetime) -> str:
        return dt.strftime("%d/%m/%Y")


class UserOrganization(DynamicObjectType):
    org_uid = graphene.NonNull(graphene.String)
    role = graphene.NonNull(graphene.String)
    status = graphene.String(required=False)
    organization = graphene.Field(Organization, required=False)

    def to_json(self):
        return {"org_uid": self.org_uid, "role": self.role, "status": self.status}


class User(DynamicObjectType):
    email = graphene.NonNull(graphene.String)
    profile_picture = graphene.NonNull(graphene.String)
    role = graphene.NonNull(graphene.String)
    uid = graphene.NonNull(graphene.String)
    user_name = graphene.NonNull(graphene.String)
    organizations = graphene.List(graphene.String, required=False)
    user_organizations = graphene.List(UserOrganization, required=False)
    company = graphene.String(required=False)
    userRole = graphene.String(required=False)
    getInfo = graphene.Boolean()
    settings = graphene.JSONString(
        required=False, json_input=graphene.JSONString(required=True), key=graphene.String(required=True), value=graphene.String(required=True)
    )
    gallery_permissions = graphene.Field(GalleryPermissions, required=False)
    subscription = graphene.Field(Subscription, required=False)
    manuallyManaged = graphene.Boolean(required=False)
    leadSource = graphene.String(required=False)
    otherLeadSourceDetails = graphene.String(required=False)

    def to_json(self):
        return {
            "uid": self.uid,
            "profile_picture": self.profile_picture,
            "role": self.role,
            "company": self.company,
            "user_name": self.user_name,
            "email": self.email,
            "user_organizations": self.user_organizations,
        }


class Invitation(DynamicObjectType):
    email = graphene.String()
    token = graphene.String()
    status = graphene.String()
    org_uid = graphene.String()
    expiration_time = graphene.String()
    invitation_link = graphene.String(required=False)

    def __init__(self, email: str, expiration_time: str, token: str, status: str, org_uid: str, invitation_link: str):
        self.email = email
        self.token = token
        self.status = status
        self.org_uid = org_uid
        self.expiration_time = expiration_time
        self.invitation_link = invitation_link

    @staticmethod
    def from_json(json_obj):
        if json_obj is None:
            return None
        return Invitation(
            email=json_obj.get("email", None),
            token=json_obj.get("token", None),
            status=json_obj.get("status", None),
            org_uid=json_obj.get("org_uid", None),
            expiration_time=json_obj.get("expiration_time", None),
            invitation_link=json_obj.get("invitation_link", None),
        )


class AuthUser:
    role: str
    user_id: str

    def __init__(self, role, user_id):
        self.role = role
        self.user_id = user_id
