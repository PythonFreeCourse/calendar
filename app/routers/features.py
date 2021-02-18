from fastapi import APIRouter, Request, Depends

from app.dependencies import get_db, SessionLocal
from app.database.models import UserFeature, Feature
from app.internal.features import (
    create_association,
    is_association_exists_in_db,
    is_feature_exists_in_disabled,
    is_feature_exists_in_enabled,
    get_user_disabled_features,
    get_user_enabled_features
)

router = APIRouter(
    prefix="/features",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get('/')
async def index(
    request: Request, session: SessionLocal = Depends(get_db)
) -> list:
    features = session.query(Feature).all()
    return features


@router.post('/add')
async def add_feature_to_user(
    request: Request, session: SessionLocal = Depends(get_db)
) -> UserFeature:
    form = await request.form()

    user_id = form['user_id']  # OPTION - get active user id instead.
    feat = session.query(Feature).filter_by(id=form['feature_id']).first()

    is_exist = is_association_exists_in_db(form=form, session=session)

    if feat is None or is_exist:
        # in case there is no feature in the database with that same id
        # and or the association is exist
        return False

    association = create_association(
        db=session,
        feature_id=feat.id,
        user_id=user_id,
        is_enable=True
    )

    return session.query(UserFeature).filter_by(id=association.id).first()


@router.post('/delete')
async def delete_user_feature_association(
    request: Request,
    session: SessionLocal = Depends(get_db)
) -> bool:
    form = await request.form()

    user_id = form['user_id']  # OPTION - get active user id instead.
    feature_id = form['feature_id']

    is_exist = is_association_exists_in_db(form=form, session=session)

    if not is_exist:
        return False

    session.query(UserFeature).filter_by(
        feature_id=feature_id,
        user_id=user_id
    ).delete()
    session.commit()

    return True


@router.post('/on')
async def enable_feature(request: Request,
                         session: SessionLocal = Depends(get_db)) -> bool:
    form = await request.form()

    is_exists = is_association_exists_in_db(form=form, session=session)

    if not is_exists:
        return False

    db_association = session.query(UserFeature).filter_by(
        feature_id=form['feature_id'],
        user_id=form['user_id']
    ).first()
    db_association.is_enable = True
    session.commit()
    return True


@router.post('/off')
async def disable_feature(request: Request,
                          session: SessionLocal = Depends(get_db)) -> bool:
    form = await request.form()
    print(dict(form))
    is_exist = is_association_exists_in_db(form=form, session=session)

    if not is_exist:
        return False

    db_association = session.query(UserFeature).filter_by(
        feature_id=form['feature_id'],
        user_id=form['user_id']
    ).first()

    db_association.is_enable = False
    session.commit()

    return True


@router.get('/active')
def show_user_enabled_features(
    session: SessionLocal = Depends(get_db)
) -> list:
    return get_user_enabled_features(session=session)


@router.get('/deactive')
def show_user_disabled_features(
    session: SessionLocal = Depends(get_db)
) -> list:
    return get_user_disabled_features(session=session)


@router.get('/unlinked')
def get_user_unlinked_features(
    session: SessionLocal = Depends(get_db)
) -> list:
    data = []
    all_features = session.query(Feature).all()

    for feat in all_features:
        in_disabled = is_feature_exists_in_disabled(
            feature=feat, session=session
        )

        in_enabled = is_feature_exists_in_enabled(
            feature=feat, session=session
        )

        if not in_enabled and not in_disabled:
            data.append(feat)

    return data
