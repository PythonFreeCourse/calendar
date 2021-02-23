from fastapi import Depends, Request
from functools import wraps
from starlette.responses import RedirectResponse
from typing import List

from app.database.models import UserFeature, Feature, User
from app.dependencies import get_db, SessionLocal
from app.internal.security.dependancies import current_user_from_db
from app.internal.security.ouath2 import get_authorization_cookie
from app.internal.features_index import features
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


def create_features_at_startup(session: SessionLocal) -> bool:
    for feat in features:
        if not is_feature_exists(feature=feat, session=session):
            create_feature(**feat, db=session)
    return True


def is_association_exists_in_db(
    form: dict,
    session: SessionLocal,
    user: User,
) -> bool:
    db_association = (
        session.query(UserFeature)
        .filter_by(feature_id=form["feature_id"], user_id=user.id)
        .first()
    )

    return db_association is not None


def delete_feature(
    feature: Feature,
    session: SessionLocal = Depends(get_db),
) -> None:
    session.query(UserFeature).filter_by(feature_id=feature.id).delete()
    session.query(Feature).filter_by(id=feature.id).delete()
    session.commit()


def is_feature_exists(feature: dict, session: SessionLocal) -> bool:
    db_feature = (
        session.query(Feature)
        .filter(
            (Feature.name == feature["name"])
            | (Feature.route == feature["route"]),
        )
        .first()
    )

    return db_feature is not None


def update_feature(
    feature: Feature,
    feature_dict: dict,
    session: SessionLocal = Depends(get_db),
) -> Feature:
    feature.name = feature_dict["name"]
    feature.route = feature_dict["route"]
    feature.description = feature_dict["description"]
    feature.creator = feature_dict["creator"]
    session.commit()
    return feature


def is_feature_enabled(
    user: User,
    feature: Feature,
    session: SessionLocal = Depends(get_db),
) -> bool:
    enabled_features = get_user_enabled_features(session=session, user=user)
    return any(ef.id == feature.id for ef in enabled_features)


async def is_access_allowd(request: Request, route: str) -> bool:

    session = SessionLocal()

    # To get current user.
    # Note: can't use dependency beacause its designed for routes only.
    # Needed to it manualy.
    jwt = await get_authorization_cookie(request=request)
    user = await current_user_from_db(request=request, jwt=jwt, db=session)

    feature = session.query(Feature).filter_by(route=route).first()

    if feature is None:
        # in case there is no feature exists in the database that match the
        # route that gived by to the request.
        return True

    user_pref = (
        session.query(UserFeature)
        .filter_by(feature_id=feature.id, user_id=user.id)
        .first()
    )

    return user_pref is not None and user_pref.is_enable


def create_feature(
    name: str,
    route: str,
    description: str,
    creator: str = None,
    db: SessionLocal = Depends(),
) -> Feature:
    """Creates a feature."""
    db = SessionLocal()
    return create_model(
        db,
        Feature,
        name=name,
        route=route,
        creator=creator,
        description=description,
    )


def create_user_feature_association(
    db: SessionLocal,
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


def get_user_enabled_features(
    user_id: int,
    session: SessionLocal = Depends(get_db),
) -> List[Feature]:
    enabled = []
    user_prefs = session.query(UserFeature).filter_by(user_id=user_id).all()

    for pref in user_prefs:
        if pref.is_enable:
            feature = (
                session.query(Feature).filter_by(id=pref.feature_id).first()
            )
            enabled.append(feature)

    return enabled


async def get_user_uninstalled_features(
    request: Request,
    session: SessionLocal = Depends(get_db),
) -> List[Feature]:
    uninstalled = []
    all_features = session.query(Feature).all()

    # To get current user.
    # Note: can't use dependency beacause its designed for routes only.
    # Needed to it manualy.
    jwt = await get_authorization_cookie(request=request)
    user = await current_user_from_db(request=request, jwt=jwt, db=session)

    for feat in all_features:
        in_enabled = is_feature_enabled(
            feature=feat,
            session=session,
            user_id=user.id,
        )

        if not in_enabled:
            uninstalled.append(feat)

    return uninstalled
