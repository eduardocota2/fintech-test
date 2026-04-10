from app.db.models.user import User
from app.db.unit_of_work import SqlAlchemyUnitOfWork
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token
from app.services.errors import AuthError, ConflictError


class AuthService:
    def get_user_by_id(self, *, user_id: str) -> User | None:
        with SqlAlchemyUnitOfWork() as uow:
            if uow.users is None or uow.session is None:
                raise RuntimeError("Repository unavailable")
            return uow.session.get(User, user_id)

    def register_user(self, *, email: str, password: str, is_admin: bool) -> User:
        with SqlAlchemyUnitOfWork() as uow:
            if uow.users is None or uow.session is None:
                raise RuntimeError("Repository unavailable")

            existing = uow.users.get_by_email(email)
            if existing is not None:
                raise ConflictError("El usuario ya existe")

            user = User(
                email=email,
                password_hash=hash_password(password),
                is_admin=is_admin,
            )
            uow.users.add(user)
            uow.session.flush()
            return user

    def login(self, *, email: str, password: str) -> str:
        with SqlAlchemyUnitOfWork() as uow:
            if uow.users is None:
                raise RuntimeError("Repository unavailable")
            user = uow.users.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Credenciales inválidas")

        return create_access_token(subject=user.id, is_admin=user.is_admin)
