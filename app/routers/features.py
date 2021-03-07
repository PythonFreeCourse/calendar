from typing import List

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.sql import exists

from app.database.models import Feature, User, UserFeature
from app.dependencies import SessionLocal, get_db, templates
from app.internal.features import (
    create_user_feature_association,
    get_user_installed_features,
    get_user_uninstalled_features,
    is_user_has_feature,
    remove_follower,
)
from app.internal.security.dependencies import current_user

router = APIRouter(
    prefix="/features",
    tags=["features"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def index(
    request: Request,
    session: SessionLocal = Depends(get_db),
    user: User = Depends(current_user),
) -> templates:
    features = {
        "installed": get_user_installed_features(
            session=session,
            user_id=user.user_id,
        ),
        "uninstalled": get_user_uninstalled_features(
            session=session,
            user_id=user.user_id,
        ),
    }

    return templates.TemplateResponse(
        "features.html",
        {"request": request, "features": features},
    )


@router.post("/add")
async def add_feature_to_user(
    request: Request,
    session: SessionLocal = Depends(get_db),
    user: User = Depends(current_user),
) -> bool:
    form = await request.form()

    feat = session.query(
        exists().where(Feature.id == form["feature_id"]),
    ).scalar()

    is_exist = is_user_has_feature(
        session=session,
        feature_id=form["feature_id"],
        user_id=user.user_id,
    )

    if not feat or is_exist:
        # in case there is no feature in the database with that same id
        # and or the association is exist
        return False

    create_user_feature_association(
        db=session,
        feature_id=form["feature_id"],
        user_id=user.user_id,
        is_enable=True,
    )

    return is_user_has_feature(
        session=session,
        feature_id=form["feature_id"],
        user_id=user.user_id,
    )


@router.post("/delete")
async def delete_user_feature_association(
    request: Request,
    session: SessionLocal = Depends(get_db),
    user: User = Depends(current_user),
) -> bool:
    form = await request.form()
    feature_id = int(form["feature_id"])

    is_exist = is_user_has_feature(
        session=session,
        feature_id=feature_id,
        user_id=user.user_id,
    )

    if not is_exist:
        return False

    remove_follower(feature_id=feature_id, session=session)

    session.query(UserFeature).filter_by(
        feature_id=feature_id,
        user_id=user.user_id,
    ).delete()
    session.commit()

    return True


@router.get("/installed")
async def get_user_feature(
    request: Request,
    session: SessionLocal = Depends(get_db),
    user: User = Depends(current_user),
) -> List[Feature]:
    return get_user_installed_features(user_id=user.user_id, session=session)


@router.post("/settings/{feature_name}")
async def render_settings(
    request: Request,
    feature_name: str,
) -> HTMLResponse:
    form = await request.form()
    feature_name = "".join(feature_name.split())
    template = templates.get_template(
        "partials/features_panels/" + feature_name + "_panel.html",
    )
    if template is not None:
        content = template.render()
        return HTMLResponse(content=content)
