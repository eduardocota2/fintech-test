from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User | None:
        self.session.add(user)
        return user
    
    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.scalar(stmt)
    
    