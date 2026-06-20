from sqlalchemy.orm import Session
from src.repositories.user import UserRepository
from src.models.user import User
from src.schemas.auth import RegisterRequest, LoginRequest
from fastapi import HTTPException, status
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from src.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    @staticmethod
    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def create_access_token(user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_access_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.PyJWTError:
            return None

    def register_user(self, request: RegisterRequest) -> User:
        existing_user = self.user_repo.get_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
        
        hashed_password = self.get_password_hash(request.password)
        new_user = User(email=request.email, password_hash=hashed_password)
        return self.user_repo.create(new_user)

    def authenticate_user(self, request: LoginRequest) -> User:
        user = self.user_repo.get_by_email(request.email)
        if not user or not self.verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
