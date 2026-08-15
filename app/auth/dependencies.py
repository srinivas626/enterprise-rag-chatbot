from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User


def require_user(request: Request, db: Session = Depends(get_db)) -> User:

    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not signed in")

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Not signed in")

    return user
