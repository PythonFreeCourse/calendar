from fastapi import APIRouter, Request, Depends
from sqlalchemy import or_
from sqlalchemy.sql.expression import false

from app.dependencies import get_db, SessionLocal
from app.database.models import User, UserFeature, Feature
from app.internal.utils import create_model
from app.features.features import features


router = APIRouter(
    prefix="/features",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get('/')
def index(request: Request, session: SessionLocal = Depends(get_db)):
    features = session.query(Feature).all()
    return features


def create_features_at_startup(session: SessionLocal):

    for feat in features:
        if not is_feature_exist_in_db(feature=feat, session=session):
            create_feature(**feat, db=session)

    fs = session.query(Feature).all()

    return {'all': fs}


@router.get('/test-association')
def testAssociation(request: Request, session: SessionLocal = Depends(get_db)):
    create_association(db=session, feature_id=1, user_id=1, is_enable=True)
    create_association(db=session, feature_id=3, user_id=1, is_enable=False)

    associations = session.query(UserFeature).all()

    return {'all': associations}


def delete_feature(feature: Feature, session: SessionLocal = Depends(get_db)):
    session.query(UserFeature).filter_by(feature_id=feature.id).delete()
    session.query(Feature).filter_by(id=feature.id).delete()
    session.commit()


def is_feature_exist_in_db(feature: dict, session: SessionLocal):
    db_feature = session.query(Feature).filter(
                or_(Feature.name == feature['name'],
                    Feature.route == feature['route'])).first()

    if db_feature is not None:
        # Update if found
        update_feature(feature=db_feature,
                       new_feature_obj=feature,
                       session=session)
        return True
    return False


def update_feature(feature: Feature, new_feature_obj: dict,
                   session: SessionLocal = Depends(get_db)):

    feature.name = new_feature_obj['name']
    feature.route = new_feature_obj['route']
    feature.description = new_feature_obj['description']
    feature.creator = new_feature_obj['creator']
    session.commit()

    return feature


@router.get('/active')
def get_user_enabled_features(session: SessionLocal = Depends(get_db)):

    # TODO - get active user id
    user_id = 1

    data = []
    user_prefs = session.query(UserFeature).filter_by(user_id=user_id).all()
    for pref in user_prefs:
        if pref.is_enable:
            feature = session.query(Feature).filter_by(
                id=pref.feature_id).first()
            data.append({'feature': feature, 'is_enabled': pref.is_enable})

    return data


@router.get('/deactive')
def get_user_disabled_features(session: SessionLocal = Depends(get_db)):

    # TODO - get active user id
    user_id = 1

    data = []
    user_prefs = session.query(UserFeature).filter_by(user_id=user_id).all()
    for pref in user_prefs:
        if not pref.is_enable:
            feature = session.query(Feature).filter_by(
                id=pref.feature_id).first()
            data.append({'feature': feature, 'is_enabled': pref.is_enable})

    return data


@router.get('/unlinked')
def get_user_unlinked_features(user_id: int = 1,
                               session: SessionLocal = Depends(get_db)):
    data = []
    all_features = session.query(Feature).all()

    for feat in all_features:
        in_disabled = is_feature_exist_in_disabled(
            user_id=user_id, feature=feat, session=session
        )

        in_enabled = is_feature_exist_in_enabled(
            user_id=user_id, feature=feat, session=session
        )

        if not in_enabled and not in_disabled:
            data.append(feat)

    return data


def is_feature_exist_in_enabled(user_id: int, feature: Feature,
                                session: SessionLocal = Depends(get_db)):
    enable_features = get_user_enabled_features(session=session)

    for ef in enable_features:
        if ef['feature'].id == feature.id:
            return True

    return False


def is_feature_exist_in_disabled(user_id: int, feature: Feature,
                                 session: SessionLocal = Depends(get_db)):
    disable_features = get_user_disabled_features(session=session)

    for df in disable_features:
        if df['feature'].id == feature.id:
            return True

    return False


def is_feature_enabled(route: str):
    session = SessionLocal()

    # TODO - get active user id
    user_id = 1

    feature = session.query(Feature).filter_by(route=f'/{route}').first()

    # *This condition must be before line 168 to avoid AttributeError!*
    if feature is None:
        # in case there is no feature exist in
        # the database that match the route that passed to the request.
        return True

    user_pref = session.query(UserFeature).filter_by(
        feature_id=feature.id,
        user_id=user_id
    ).first()

    if user_pref is None:
        # in case the feature is unlinked to user
        return False
    elif user_pref.is_enable:
        # in case the feature is enabled
        return True
    # in case the feature is disabled
    return False


def create_feature(name: str, route: str,
                   description: str, creator: str = None,
                   db: SessionLocal = Depends()):
    """Creates a feature."""

    db = SessionLocal()

    feature = create_model(
        db, Feature,
        name=name,
        route=route,
        creator=creator,
        description=description
    )
    return feature


def create_association(
        db: SessionLocal, feature_id: int, user_id: int, is_enable: bool):
    """Creates an association."""

    association = create_model(
        db, UserFeature,
        user_id=user_id,
        feature_id=feature_id,
        is_enable=is_enable
    )

    return association
