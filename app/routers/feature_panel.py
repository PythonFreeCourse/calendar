from os import name
from fastapi import APIRouter, Request, Depends
from app.database.database import get_db, SessionLocal
from app.database.models import User, UserFeature, Feature
from app.database.models import Base


router = APIRouter(
    prefix="/features",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get('/')
def panel_index(request: Request, session: SessionLocal = Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()
    feature = create_feature(db=session, name='google1', route='/profile1',
                             user=user, is_enable=False)
    session.commit()
    session.query(UserFeature).filter_by(feature_id=8).delete()
    session.commit()
    return user.features
    obj = session.query(Feature).all()

    return {"hello": "world", "feature": obj}


def create_feature(db, name, route, user, is_enable):
    """Creates an event and an association."""

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


def save(item, session: SessionLocal) -> bool:
    """Commits an instance to the db.
    source: app.database.database.Base"""

    if issubclass(item.__class__, Base):
        session.add(item)
        session.commit()
        return True
    return False


def create_model(session: SessionLocal, model_class, **kw):
    """Creates and saves a db model."""

    instance = model_class(**kw)
    save(instance, session)
    return instance
