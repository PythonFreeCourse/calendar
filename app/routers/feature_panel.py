from fastapi import APIRouter, Request, Depends
from sqlalchemy import or_

from app.database.database import get_db, SessionLocal
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
        db_feature.name = feature['name']
        db_feature.route = feature['route']
        db_feature.description = feature['description']
        db_feature.creator = feature['creator']
        session.commit()
        return True
    return False


def update_feature(feature: Feature, new_feature_obj: dict,
                   session: SessionLocal = Depends(get_db)):
    # need a run
    feature.name = new_feature_obj['name']
    feature.route = new_feature_obj['route']
    feature.description = new_feature_obj['description']
    feature.creator = new_feature_obj['creator']
    session.commit()


@router.get('/active')
def get_user_enabled_features(user_id: int = 1,
                              session: SessionLocal = Depends(get_db)):
    data = []
    user_prefs = session.query(UserFeature).filter_by(user_id=user_id).all()
    for pref in user_prefs:
        if pref.is_enable:
            feature = session.query(Feature).filter_by(
                id=pref.feature_id).first()
            data.append({'feature': feature, 'is_enabled': pref.is_enable})

    return data


@router.get('/deactive')
def get_user_disabled_features(user_id: int = 1,
                               session: SessionLocal = Depends(get_db)):
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
    return data


def is_feature_enabled(route: str):
    session = SessionLocal()
    # TODO - get active user id
    user = session.query(User).filter_by(id=1).first()

    feature = session.query(Feature).filter_by(route=f'/{route}').first()
    user_pref = session.query(UserFeature).filter_by(
                feature_id=feature.id,
                user_id=user.id
                ).first()
    if feature is None:
        return False
    elif user_pref is not None and user_pref.is_enable or user_pref is None:
        return True
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
