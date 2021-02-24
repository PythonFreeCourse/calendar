from fastapi import APIRouter, Request, Depends

from app.dependencies import get_db, SessionLocal, templates
from app.database.models import User, UserFeature, Feature
from app.internal.security.dependencies import current_user_from_db
from app.internal.features import (
    create_user_feature_association,
    is_association_exists_in_db,
    get_user_uninstalled_features,
    get_user_enabled_features,
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
    user: User = Depends(current_user_from_db),
) -> templates:
    features = {
        "installed": get_user_enabled_features(
            session=session, user_id=user.id,
        ),
        "uninstalled": await get_user_uninstalled_features(
            session=session, request=request,
        ),
    }

    return templates.TemplateResponse(
        "features.html", {"request": request, "features": features},
    )


@router.post("/add")
async def add_feature_to_user(
    request: Request,
    session: SessionLocal = Depends(get_db),
    user: User = Depends(current_user_from_db),
) -> UserFeature or bool:
    form = await request.form()

    feat = session.query(Feature).filter_by(id=form["feature_id"]).first()

    is_exist = is_association_exists_in_db(
        form=form,
        session=session,
        user=user,
    )

    if feat is None or is_exist:
        # in case there is no feature in the database with that same id
        # and or the association is exist
        return False

    association = create_user_feature_association(
        db=session,
        feature_id=feat.id,
        user_id=user.id,
        is_enable=True,
    )

    return session.query(UserFeature).filter_by(id=association.id).first()


@router.post("/delete")
async def delete_user_feature_association(
    request: Request,
    session: SessionLocal = Depends(get_db),
    user: User = Depends(current_user_from_db),
) -> bool:
    form = await request.form()
    feature_id = form["feature_id"]

    is_exist = is_association_exists_in_db(
        form=form,
        session=session,
        user=user,
    )

    if not is_exist:
        return False

    remove_follower(feature_id=feature_id, session=session)

    session.query(UserFeature).filter_by(
        feature_id=feature_id,
        user_id=user.id,
    ).delete()
    session.commit()

    return True
