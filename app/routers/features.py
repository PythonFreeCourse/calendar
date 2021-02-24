from fastapi import APIRouter, Request, Depends
from sqlalchemy.sql import exists

from app.dependencies import get_db, SessionLocal, templates
from app.database.models import User, UserFeature, Feature
from app.internal.security.dependencies import current_user
from app.internal.features import (
    create_user_feature_association,
    get_user_uninstalled_features,
    get_user_installed_features,
    is_user_has_feature,
    remove_follower,
)

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
        "uninstalled": await get_user_uninstalled_features(
            session=session,
            request=request,
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
