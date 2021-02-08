from fastapi import APIRouter, Request, Depends
from app.database.database import get_db, SessionLocal
from app.database.models import User, UserFeature, Feature
from app.internal.utils import create_model


router = APIRouter(
    prefix="/features",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get('/')
def get_feature_panel(request: Request,
                      session: SessionLocal = Depends(get_db)):
    features = session.query(Feature).all()
    return features


@router.get('/create-test')
def test_insert(request: Request, session: SessionLocal = Depends(get_db)):

    delete_all_feature(session)
    user = session.query(User).filter_by(id=1).first()
    create_feature(
                    db=session, name='profile',
                    route='/profile',
                    user=user, is_enable=True,
                  )
    create_feature(
                    db=session, name='feature-panel',
                    route='/features',
                    user=user, is_enable=True
                  )

    return {'all': user.features}


def delete_feature(feature: Feature, session: SessionLocal = Depends(get_db)):
    session.query(UserFeature).filter_by(feature_id=feature.id).delete()
    session.query(Feature).filter_by(id=feature.id).delete()
    session.commit()


def delete_all_feature(session: SessionLocal = Depends(get_db)):
    session.query(UserFeature).delete()
    session.query(Feature).delete()
    session.commit()


def cleanup_existing_features():
    pass


def is_feature_enabled(route: str, user: int, session: SessionLocal):
    feature = session.query(Feature).filter_by(route=f'/{route}').first()
    user_pref = session.query(UserFeature).filter_by(
                feature_id=feature.id,
                user_id=user.id
                ).first()

    if feature is None:
        return False
    elif user_pref is not None and user_pref.is_enable:
        return True
    return False


def create_feature(db: SessionLocal, name: str, route: str,
                   user: User, is_enable: bool):
    """Creates a feature and an association."""

    feature = create_model(
        db, Feature,
        name=name,
        route=route,
    )
    create_model(
        db, UserFeature,
        user_id=user.id,
        feature_id=feature.id,
        is_enable=is_enable
    )
    return feature
