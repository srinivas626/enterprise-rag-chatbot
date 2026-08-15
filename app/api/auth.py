from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.oauth import oauth
from app.auth.dependencies import require_user
from app.db import get_db
from app.models.user import User


router = APIRouter(prefix="/auth")

SUPPORTED_PROVIDERS = {"google", "github", "yahoo"}


@router.get("/login/{provider}")
async def login(provider: str, request: Request):

    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unknown provider")

    client = oauth.create_client(provider)
    redirect_uri = request.url_for("auth_callback", provider=provider)

    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}", name="auth_callback")
async def auth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):

    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unknown provider")

    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)

    provider_user_id, email, name = await _extract_identity(provider, client, token)

    user = (
        db.query(User)
        .filter(
            User.provider == provider,
            User.provider_user_id == provider_user_id
        )
        .first()
    )

    if user is None:
        user = User(
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    request.session["user_id"] = user.id

    return RedirectResponse(url="/")


@router.get("/me")
def me(user: User = Depends(require_user)):

    return {
        "id": user.id,
        "provider": user.provider,
        "email": user.email,
        "name": user.name,
    }


@router.post("/logout")
def logout(request: Request):

    request.session.clear()

    return {"message": "Logged out"}


async def _extract_identity(provider: str, client, token: dict):

    if provider == "github":

        resp = await client.get("user", token=token)
        profile = resp.json()

        provider_user_id = str(profile["id"])
        name = profile.get("name") or profile.get("login")
        email = profile.get("email")

        if not email:
            emails_resp = await client.get("user/emails", token=token)
            emails = emails_resp.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary["email"] if primary else None

        return provider_user_id, email, name

    userinfo = token.get("userinfo")

    if userinfo is None:
        userinfo = await client.parse_id_token(token)

    return userinfo["sub"], userinfo.get("email"), userinfo.get("name")
