from enum import Enum

import graphene


class VDRImageState(Enum):
    ERROR = "ERROR"
    CLASSIFYING = "CLASSIFYING"
    CLASSIFIED = "CLASSIFIED"


class ServiceName(Enum):
    CLASSIFICATION = "CLASSIFICATION"
    BRIATOR = "BRIATOR"
    JORMUNGANDR = "JORMUNGANDR"
    BACKGROUND_LIVELINESS = "BACKGROUND_LIVELINESS"
    FACE_LIVELINESS = "FACE_LIVELINESS"
    CAMERA_MOTION = "CAMERA_MOTION"
    TRITON = "TRITON"


class UserRoles(Enum):
    ADMIN = "admin"
    VIEWER = "view"
    EXTERNAL = "external"
    NON = "non"


class SubscriptionTypes(Enum):
    FREE = "free"
    PRO = "pro"
    ULTIMATE = "ultimate"


class ApiSubscriptionTypes(Enum):
    STARTER = "starter"
    BASIC = "basic"
    PRO = "pro"
    ULTIMATE = "ultimate"
    CUSTOM = "custom"
    NONE = "none"


class ApiSubscriptionStatuses(Enum):
    ACTIVE = "active"
    NOT_ACTIVE = "not_active"


class SubscriptionPeriods(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    DEFAULT = ""


class ApiKeyStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class ApiKeyTypes(Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    INTERNAL = "internal"
    IFRAME = "iframe"
    FIGMA_PLUGIN = "figma_plugin"
    PHOTOSHOP_PLUGIN = "photoshop_plugin"
    COMFY = "comfy"
    MCP = "mcp"


class OrgUserRoles(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    ADMIN_HIDDEN = "admin hidden"
    USER_HIDDEN = "user hidden"

    @staticmethod
    def all_roles():
        return list(OrgUserRoles)

    @staticmethod
    def editor_roles():
        return [OrgUserRoles.ADMIN, OrgUserRoles.ADMIN_HIDDEN, OrgUserRoles.OWNER]

    @staticmethod
    def hidden_roles():
        return [OrgUserRoles.ADMIN_HIDDEN, OrgUserRoles.USER_HIDDEN]

    @staticmethod
    def owner_roles():
        return [OrgUserRoles.OWNER]


class OrgUserStatus(Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class InvitationStatus(Enum):
    ACTIVE = "active"
    INVALID = "invalid"


class LeadSourceEnum(graphene.Enum):
    GOOGLE_SEARCH = "google_search"
    SOCIAL_MEDIA = "social_media"
    HUGGING_FACE = "hugging_face"
    GITHUB = "github"
    EVENT_CONFERENCE = "event_conference"
    OTHER = "other"
