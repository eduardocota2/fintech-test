class ServiceError(Exception):
    pass


class NotFoundError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class ForbiddenError(ServiceError):
    pass


class AuthError(ServiceError):
    pass


class InvalidTransitionError(ServiceError):
    pass