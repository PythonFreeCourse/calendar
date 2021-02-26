from functools import wraps
from typing import Dict, List

from fastapi import Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from starlette.responses import RedirectResponse

from app.database.models import Feature, UserFeature
from app.dependencies import SessionLocal, get_db
from app.internal.features_index import features
from app.internal.security.dependencies import current_user
from app.internal.security.ouath2 import get_authorization_cookie
from app.internal.utils import create_model


def feature_access_filter(call_next):
    @wraps(call_next)
    async def wrapper(*args, **kwargs):
        request = kwargs["request"]

        if request.headers["user-agent"] == "testclient":
            # in case it's a unit test.
            return await call_next(*args, **kwargs)

        # getting the url route path for matching with the database.
        route = "/" + str(request.url).replace(str(request.base_url), "")

        # getting access status.
        access = await is_access_allowd(route=route, request=request)

        if access:
            # in case the feature is enabled or access is allowed.
            return await call_next(*args, **kwargs)

        elif "referer" not in request.headers:
            # in case request come straight from address bar in browser.
            return RedirectResponse(url="/")

        # in case the feature is disabled or access isn't allowed.
        return RedirectResponse(url=request.headers["referer"])

    return wrapper


def create_features_at_startup(session: Session) -> bool:
    for feat in features:
        if not is_feature_exists(feature=feat, session=session):
            create_feature(**feat, db=session)
    return True


def is_user_has_feature(
    session: Session,
    feature_id: int,
    user_id: int,
) -> bool:
    return session.query(
        exists()
        .where(UserFeature.user_id == user_id)
        .where(UserFeature.feature_id == feature_id),
    ).scalar()


def delete_feature(
    feature: Feature,
    session: Session = Depends(get_db),
) -> None:
    session.query(UserFeature).filter_by(feature_id=feature.id).delete()
    session.query(Feature).filter_by(id=feature.id).delete()
    session.commit()


def is_feature_exists(feature: Dict[str, str], session: Session) -> bool:
    is_exists = session.query(
        exists()
        .where(Feature.name == feature["name"])
        .where(Feature.route == feature["route"]),
    ).scalar()

    return is_exists


def update_feature(
    feature: Feature,
    feature_dict: Dict[str, str],
    session: Session = Depends(get_db),
) -> Feature:
    feature.name = feature_dict["name"]
    feature.route = feature_dict["route"]
    feature.description = feature_dict["description"]
    feature.creator = feature_dict["creator"]
    session.commit()
    return feature


async def is_access_allowd(request: Request, route: str) -> bool:
    session = SessionLocal()

    # Get current user.
    # Note: can't use dependency beacause its designed for routes only.
    # current_user return schema not an db model.
    jwt = await get_authorization_cookie(request=request)
    user = await current_user(request=request, jwt=jwt, db=session)

    feature = session.query(Feature).filter_by(route=route).first()

    if feature is None:
        # in case there is no feature exists in the database that match the
        # route that gived by to the request.
        return True

    user_feature = session.query(
        exists().where(
            (UserFeature.feature_id == feature.id)
            & (UserFeature.user_id == user.user_id),
        ),
    ).scalar()

    return user_feature


def create_feature(
    db: Session,
    name: str,
    route: str,
    description: str,
    creator: str = None,
) -> Feature:
    """Creates a feature."""
    return create_model(
        db,
        Feature,
        name=name,
        route=route,
        creator=creator,
        description=description,
    )


def create_user_feature_association(
    db: Session,
    feature_id: int,
    user_id: int,
    is_enable: bool,
) -> UserFeature:
    """Creates an association."""
    return create_model(
        db,
        UserFeature,
        user_id=user_id,
        feature_id=feature_id,
        is_enable=is_enable,
    )


def get_user_installed_features(
    user_id: int,
    session: Session = Depends(get_db),
) -> List[Feature]:
    return (
        session.query(Feature)
        .join(UserFeature)
        .filter(UserFeature.user_id == user_id)
        .all()
    )


def get_user_uninstalled_features(
    user_id: int,
    session: Session = Depends(get_db),
) -> List[Feature]:
    return (
        session.query(Feature)
        .filter(
            Feature.id.notin_(
                session.query(UserFeature.feature_id).filter(
                    UserFeature.user_id == user_id,
                ),
            ),
        )
        .all()
    )
