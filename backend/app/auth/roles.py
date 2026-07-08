from app.utils.enums import UserRole


ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.ADMIN: 3,
    UserRole.ENGINEER: 2,
    UserRole.MANAGER: 1,
}


def role_has_permission(user_role: UserRole, required_role: UserRole) -> bool:
    """Check if a user role meets the required role level."""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)
