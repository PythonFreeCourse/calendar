from app.database.models import Feature
import pytest
import app.internal.features as internal
import app.routers.features as route


@pytest.fixture
def mock_features():
    return [
        {
            "name": 'test',
            "route": '/',
            "description": 'testing',
            "creator": 'test'
        }
    ]


def test_create_features_at_startup(mocker, session, mock_features):

    mocker.patch(
        'app.internal.features.features',
        mock_features
    )
    mocker.patch(
        'app.internal.features.is_feature_exist_in_db',
        return_value=False
    )

    assert internal.create_features_at_startup(session)


def test_create_association(session):
    assert internal.create_association(
        db=session, feature_id=1, user_id=1, is_enable=False
    ) is not None


def test_get_user_enabled_features(session):

    internal.create_feature(
        db=session, name='name', route="route",
        creator='creator', description='description')

    internal.create_association(
        db=session, feature_id=1, user_id=1, is_enable=True)

    assert internal.get_user_enabled_features(session)[0].get(
        'is_enabled') is True


def test_get_user_disabled_features(session):

    internal.create_feature(
        db=session, name='name', route="route",
        creator='creator', description='description')

    internal.create_association(
        db=session, feature_id=1, user_id=1, is_enable=False)

    assert internal.get_user_disabled_features(session)[0].get(
        'is_enabled') is False


def test_is_association_exist_in_db(session):
    internal.create_association(
        db=session, feature_id=1, user_id=1, is_enable=False)

    form_mock = {
        'feature_id': 1,
        'user_id': 1
    }
    assert internal.is_association_exist_in_db(form_mock, session)


def test_delete_feature(session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )
    session.add(test)
    session.commit()

    feat = session.query(Feature).filter_by(name=test.name).first()

    internal.delete_feature(feature=feat, session=session)

    feat = session.query(Feature).filter_by(name=test.name).first()

    assert feat is None


def test_is_feature_exist_in_db(mocker, session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )
    session.add(test)
    session.commit()

    update = {
        'name': 'test',
        'route': '/route',
        'description': 'update',
        'creator': 'test'
    }

    assert internal.is_feature_exist_in_db(update, session)


def test_update_feature(session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    update = {
        'name': 'test',
        'route': '/route',
        'description': 'update',
        'creator': 'test'
    }

    feature = internal.update_feature(test, update, session)

    assert feature.description == 'update'


def test_is_feature_exist_in_enabled(session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    feat = session.query(Feature).filter_by(name=test.name).first()

    internal.create_association(
        db=session, feature_id=feat.id, user_id=1, is_enable=True)

    assert internal.is_feature_exist_in_enabled(feat, session)


def test_is_feature_exist_in_disabled(mocker, session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    feat = session.query(Feature).filter_by(name=test.name).first()

    internal.create_association(
        db=session, feature_id=feat.id, user_id=1, is_enable=False)

    assert internal.is_feature_exist_in_disabled(feat, session)


def test_is_feature_enabled(mocker, session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    feat = session.query(Feature).filter_by(name=test.name).first()

    internal.create_association(
        db=session, feature_id=feat.id, user_id=1, is_enable=True)

    mocker.patch(
        'app.internal.features.SessionLocal',
        return_value=session
    )
    assert internal.is_feature_enabled(route='/route') is True


def test_create_feature(session):

    feat = internal.create_feature(
        name='test', route='/route', description='testing', creator='test'
    )

    assert feat.name == 'test'


@pytest.mark.asyncio
async def test_index(features_test_client):
    url = route.router.url_path_for('index')

    resp = await features_test_client.get(url)
    assert resp.ok


@pytest.mark.asyncio
async def test_add_feature_to_user(features_test_client, session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    url = route.router.url_path_for('add_feature_to_user')

    resp = await features_test_client.post(url, form={
        'feature_id': 1,
        'user_id': 1
    })
    assert resp.ok


@pytest.mark.asyncio
async def test_delete_user_feature_association(features_test_client, session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    feat = session.query(Feature).filter_by(name=test.name).first()

    internal.create_association(
        db=session, feature_id=feat.id, user_id=1, is_enable=True)

    url = route.router.url_path_for('delete_user_feature_association')

    resp = await features_test_client.post(url, form={
        'feature_id': 1,
        'user_id': 1
    })
    assert resp.ok
    assert resp.content == b'true'


@pytest.mark.asyncio
async def test_enable_feature(features_test_client, session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    feat = session.query(Feature).filter_by(name=test.name).first()

    internal.create_association(
        db=session, feature_id=feat.id, user_id=1, is_enable=False)

    url = route.router.url_path_for('enable_feature')

    resp = await features_test_client.post(url, form={
        'feature_id': 1,
        'user_id': 1
    })
    assert resp.ok
    assert resp.content == b'true'


@pytest.mark.asyncio
async def test_disable_feature(features_test_client, session):
    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    feat = session.query(Feature).filter_by(name=test.name).first()

    internal.create_association(
        db=session, feature_id=feat.id, user_id=1, is_enable=False)

    url = route.router.url_path_for('disable_feature')

    resp = await features_test_client.post(url, form={
        'feature_id': 1,
        'user_id': 1
    })
    assert resp.ok
    assert resp.content == b'true'


@pytest.mark.asyncio
async def test_show_user_enabled_features(mocker, features_test_client):

    mocker.patch(
        'app.routers.features.get_user_enabled_features',
        return_value=True
    )

    url = route.router.url_path_for('show_user_enabled_features')

    resp = await features_test_client.get(url)
    assert resp.ok
    assert resp.content == b'true'


@pytest.mark.asyncio
async def test_show_user_disabled_features(mocker, features_test_client):

    mocker.patch(
        'app.routers.features.get_user_disabled_features',
        return_value=True
    )

    url = route.router.url_path_for('show_user_disabled_features')

    resp = await features_test_client.get(url)
    assert resp.ok
    assert resp.content == b'true'


@pytest.mark.asyncio
async def test_get_user_unlinked_features(
        mocker, features_test_client, session):

    test = Feature(
        name='test',
        route='/route',
        description='testing',
        creator='test'
    )

    session.add(test)
    session.commit()

    mocker.patch(
        'app.routers.features.get_user_disabled_features',
        return_value=True
    )

    url = route.router.url_path_for('get_user_unlinked_features')

    resp = await features_test_client.get(url)
    assert resp.ok
    json_resp = resp.json()[0]
    assert json_resp['id'] == 1
