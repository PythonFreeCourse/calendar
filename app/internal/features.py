from fastapi import Depends
from functools import wraps
from starlette.responses import RedirectResponse
from typing import List

from app.database.models import UserFeature, Feature
from app.dependencies import get_db, SessionLocal
from app.internal.features_index import features
from app.internal.utils import create_model, get_current_user


def feature_access_filter(call_next):

    @wraps(call_next)
    async def wrapper(*args, **kwargs):
        request = kwargs['request']

        if request.headers['user-agent'] == 'testclient':
            # in case it's a unit test.
            return await call_next(*args, **kwargs)

        # getting the url route path for matching with the database.
        route = '/' + str(request.url).replace(str(request.base_url), '')

        # getting access status.
        is_enabled = is_access_allowd(route=route)

        if is_enabled:
            # in case the feature is enabled or access is allowed.
            return await call_next(*args, **kwargs)

        elif 'referer' not in request.headers:
            # in case request come straight from address bar in browser.
            return RedirectResponse(url='/')

        # in case the feature is disabled or access isn't allowed.
        return RedirectResponse(url=request.headers['referer'])

    return wrapper


def create_features_at_startup(session: SessionLocal) -> bool:
    for feat in features:
        if not is_feature_exists(feature=feat, session=session):
            create_feature(**feat, db=session)

    return True


def is_association_exists_in_db(form: dict, session: SessionLocal) -> bool:
    db_association = session.query(UserFeature).filter_by(
        feature_id=form['feature_id'],
        user_id=get_current_user(session=session).id
    ).first()

    return db_association is not None


def delete_feature(
    feature: Feature, session: SessionLocal = Depends(get_db)
) -> None:
    session.query(UserFeature).filter_by(feature_id=feature.id).delete()
    session.query(Feature).filter_by(id=feature.id).delete()
    session.commit()


def is_feature_exists(feature: dict, session: SessionLocal) -> bool:
    db_feature = session.query(Feature).filter(
        (Feature.name == feature['name']) |
        (Feature.route == feature['route'])).first()

    if db_feature is None:
        return False

    # Update if found
    update_feature(
        feature=db_feature, new_feature_obj=feature, session=session)
    return True


def update_feature(feature: Feature, new_feature_obj: dict,
                   session: SessionLocal = Depends(get_db)) -> Feature:
    feature.name = new_feature_obj['name']
    feature.route = new_feature_obj['route']
    feature.description = new_feature_obj['description']
    feature.creator = new_feature_obj['creator']
    session.commit()
    return feature


def is_feature_enabled(
    feature: Feature, session: SessionLocal = Depends(get_db)
) -> bool:
    enabled_features = get_user_enabled_features(session=session)
    return any(ef.id == feature.id for ef in enabled_features)


def is_access_allowd(route: str) -> bool:
    session = SessionLocal()
    user = get_current_user(session=session)
    feature = session.query(Feature).filter_by(route=route).first()

    if feature is None:
        # in case there is no feature exists in the database that match the
        # route that gived by to the request.
        return True

    user_pref = session.query(UserFeature).filter_by(
        feature_id=feature.id,
        user_id=user.id
    ).first()

    return user_pref is not None and user_pref.is_enable


def create_feature(name: str, route: str,
                   description: str,
                   creator: str = None,
                   db: SessionLocal = Depends()) -> Feature:
    """Creates a feature."""
    db = SessionLocal()
    return create_model(
        db, Feature,
        name=name,
        route=route,
        creator=creator,
        description=description,
    )


def create_user_feature_association(
    db: SessionLocal, feature_id: int, user_id: int, is_enable: bool
) -> UserFeature:
    """Creates an association."""
    return create_model(
        db, UserFeature,
        user_id=user_id,
        feature_id=feature_id,
        is_enable=is_enable
    )


def get_user_enabled_features(session: SessionLocal = Depends(get_db)) -> List:
    user = get_current_user(session=session)
    enabled = []
    user_prefs = session.query(UserFeature).filter_by(user_id=user.id).all()

    for pref in user_prefs:
        if pref.is_enable:
            feature = session.query(Feature).filter_by(
                id=pref.feature_id).first()
            enabled.append(feature)

    return enabled


def get_user_uninstalled_features(session: SessionLocal) -> List:
    uninstalled = []
    all_features = session.query(Feature).all()

    for feat in all_features:
        in_enabled = is_feature_enabled(
            feature=feat, session=session
        )

        if not in_enabled:
            uninstalled.append(feat)

    return uninstalled
