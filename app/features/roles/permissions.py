from enum import Enum


class Permission(str, Enum):
    # Post permissions
    POST_CREATE = "post:create"
    POST_EDIT_OWN = "post:edit_own"
    POST_EDIT_ANY = "post:edit_any"
    POST_PUBLISH = "post:publish"
    POST_DELETE_OWN = "post:delete_own"
    POST_DELETE_ANY = "post:delete_any"

    # Comment permissions
    COMMENT_CREATE = "comment:create"
    COMMENT_DELETE_OWN = "comment:delete_own"
    COMMENT_DELETE_ANY = "comment:delete_any"

    # User permissions
    USER_BAN = "user:ban"

    # Admin permissions
    ADMIN_DASHBOARD = "admin:dashboard"


#  Role → Permission matrix (matches your screenshot exactly)
ROLE_PERMISSIONS = {
    "reader": [
        Permission.COMMENT_CREATE,
        Permission.COMMENT_DELETE_OWN,
    ],
    "author": [
        Permission.POST_CREATE,
        Permission.POST_EDIT_ANY,
        Permission.POST_EDIT_OWN,
        Permission.POST_DELETE_OWN,
        Permission.COMMENT_CREATE,
        Permission.COMMENT_DELETE_OWN,
        Permission.POST_PUBLISH,
        Permission.COMMENT_DELETE_ANY,
    ],
    "editor": [
        Permission.POST_CREATE,
        Permission.POST_EDIT_OWN,
        Permission.POST_EDIT_ANY,
        Permission.POST_PUBLISH,
        Permission.POST_DELETE_OWN,
        Permission.COMMENT_CREATE,
        Permission.COMMENT_DELETE_OWN,
        Permission.COMMENT_DELETE_ANY,
    ],
    "admin": [
        Permission.POST_CREATE,
        Permission.POST_EDIT_OWN,
        Permission.POST_EDIT_ANY,
        Permission.POST_PUBLISH,
        Permission.POST_DELETE_OWN,
        Permission.POST_DELETE_ANY,
        Permission.COMMENT_CREATE,
        Permission.COMMENT_DELETE_OWN,
        Permission.COMMENT_DELETE_ANY,
        Permission.USER_BAN,
        Permission.ADMIN_DASHBOARD,
    ],
}