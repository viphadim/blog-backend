from enum import Enum


class Scope(str, Enum):
    #   Post scopes
    POST_CREATE = "post:create"
    POST_EDIT_OWN = "post:edit_own"
    POST_EDIT_ANY = "post:edit_any"
    POST_PUBLISH = "post:publish"
    POST_DELETE_OWN = "post:delete_own"
    POST_DELETE_ANY = "post:delete_any"

    #   Comment scopes
    COMMENT_CREATE = "comment:create"
    COMMENT_DELETE_OWN = "comment:delete_own"
    COMMENT_DELETE_ANY = "comment:delete_any"

    #   User scopes
    USER_BAN = "user:ban"

    #   Admin scopes
    ADMIN_DASHBOARD = "admin:dashboard"

    #   Profile scopes
    ME_READ = "me:read"
    ME_WRITE = "me:write"


#   Role → Scopes matrix
ROLE_SCOPES: dict[str, list[Scope]] = {
    "reader": [
        Scope.ME_READ,
        Scope.ME_WRITE,
        Scope.COMMENT_CREATE,
        Scope.COMMENT_DELETE_OWN,
    ],
    "author": [
        Scope.ME_READ,
        Scope.ME_WRITE,
        Scope.POST_CREATE,
        Scope.POST_EDIT_OWN,
        Scope.POST_DELETE_OWN,
        Scope.COMMENT_CREATE,
        Scope.COMMENT_DELETE_OWN,
    ],
    "editor": [
        Scope.ME_READ,
        Scope.ME_WRITE,
        Scope.POST_CREATE,
        Scope.POST_EDIT_OWN,
        Scope.POST_EDIT_ANY,
        Scope.POST_PUBLISH,
        Scope.POST_DELETE_OWN,
        Scope.COMMENT_CREATE,
        Scope.COMMENT_DELETE_OWN,
        Scope.COMMENT_DELETE_ANY,
    ],
    "admin": [
        Scope.ME_READ,
        Scope.ME_WRITE,
        Scope.POST_CREATE,
        Scope.POST_EDIT_OWN,
        Scope.POST_EDIT_ANY,
        Scope.POST_PUBLISH,
        Scope.POST_DELETE_OWN,
        Scope.POST_DELETE_ANY,
        Scope.COMMENT_CREATE,
        Scope.COMMENT_DELETE_OWN,
        Scope.COMMENT_DELETE_ANY,
        Scope.USER_BAN,
        Scope.ADMIN_DASHBOARD,
    ],
}