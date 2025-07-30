from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from authentication_file.token_op import SECURITY_KEY, ALGORITHM
from sqlalchemy.orm import Session
from database_file import database, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

# Strict user check (for protected endpoints)
def get_current_user(token: str = Depends(oauth2_scheme), db : Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.Users).filter(models.Users.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user_optional(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(database.get_db)) -> Optional[models.Users]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    user = db.query(models.Users).filter(models.Users.email == email).first()
    if user is None or user.active_status is False:
        return None

    return user

def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    user = get_current_user(token, db)
    if not user.active_status:
        raise HTTPException(status_code=403, detail="Inactive user.")
    return user

def require_roles(*roles):
    def role_checker(current_user: models.Users = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Access denied.")
        return current_user
    return role_checker
