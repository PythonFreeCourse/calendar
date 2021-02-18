from fastapi import Depends

from app.database.models import UserFeature, Feature
from app.dependencies import get_db, SessionLocal
from app.features.index import features, icons
from app.internal.utils import create_model, get_current_user


def create_features_at_startup(session: SessionLocal) -> bool:
    for feat in features:
        if not is_feature_exists_in_db(feature=feat, session=session):
            icon = icons.get(feat['name'])
            create_feature(**feat, icon=icon, db=session)

    return True


def is_association_exists_in_db(form: dict, session: SessionLocal) -> bool:
    db_association = session.query(UserFeature).filter_by(
        feature_id=form['feature_id'],
        user_id=form['user_id']
    ).first()

    return db_association is not None


def delete_feature(
    feature: Feature, session: SessionLocal = Depends(get_db)
) -> None:
    session.query(UserFeature).filter_by(feature_id=feature.id).delete()
    session.query(Feature).filter_by(id=feature.id).delete()
    session.commit()


def is_feature_exists_in_db(feature: dict, session: SessionLocal) -> bool:
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

    icon = icons.get(feature.name)
    if icon is None:
        icon = "extension-puzzle"

    feature.icon = icon
    session.commit()

    return feature


def is_feature_exists_in_enabled(
    feature: Feature, session: SessionLocal = Depends(get_db)
) -> bool:
    enabled_features = get_user_enabled_features(session=session)
    return any(ef['feature'].id == feature.id for ef in enabled_features)


def is_feature_exists_in_disabled(
    feature: Feature, session: SessionLocal = Depends(get_db)
) -> bool:
    disable_features = get_user_disabled_features(session=session)
    return any(ef['feature'].id == feature.id for ef in disable_features)


def is_feature_enabled(route: str) -> bool:
    session = SessionLocal()

    user = get_current_user(session=session)

    feature = session.query(Feature).filter_by(route=route).first()

    # *This condition must be before line 168 to avoid AttributeError!*
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
                   icon: str = None,
                   db: SessionLocal = Depends()) -> Feature:
    """Creates a feature."""

    db = SessionLocal()

    if icon is None:
        icon = "extension-puzzle"

    feature = create_model(
        db, Feature,
        name=name,
        route=route,
        creator=creator,
        description=description,
        icon=icon
    )
    return feature


def create_association(
    db: SessionLocal, feature_id: int, user_id: int, is_enable: bool
) -> UserFeature:
    """Creates an association."""

    association = create_model(
        db, UserFeature,
        user_id=user_id,
        feature_id=feature_id,
        is_enable=is_enable
    )

    return association


def get_user_enabled_features(session: SessionLocal = Depends(get_db)) -> list:
    user = get_current_user(session=session)

    data = []

    user_prefs = session.query(UserFeature).filter_by(user_id=user.id).all()
    for pref in user_prefs:
        if pref.is_enable:
            feature = session.query(Feature).filter_by(
                id=pref.feature_id).first()
            data.append({'feature': feature, 'is_enabled': pref.is_enable})

    return data


def get_user_disabled_features(
    session: SessionLocal = Depends(get_db)
) -> list:
    user = get_current_user(session=session)

    data = []
    user_prefs = session.query(UserFeature).filter_by(user_id=user.id).all()
    for pref in user_prefs:
        if not pref.is_enable:
            feature = session.query(Feature).filter_by(
                id=pref.feature_id).first()
            data.append({'feature': feature, 'is_enabled': pref.is_enable})

    return data
