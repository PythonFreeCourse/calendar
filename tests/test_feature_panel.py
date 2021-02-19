from app.database.models import Feature, UserFeature
import pytest
import app.internal.features as internal
import app.routers.features as route


@pytest.fixture
def mock_features():
    return [
        {
            "name": 'test',
            "route": '/test',
            "description": 'testing',
            "creator": 'test'
        }
    ]


@pytest.fixture
@pytest.mark.usefixtures('session')
def feature(session):
    test = Feature(
        name='test',
        route='/test',
        description='testing',
        creator='test',
        icon='test'
    )

    session.add(test)
    session.commit()

    yield test

    session.query(Feature).delete()
    session.commit()


@pytest.fixture
@pytest.mark.usefixtures('session')
def association_off(session, user):
    test = UserFeature(
        feature_id=1, user_id=user.id, is_enable=False)

    session.add(test)
    session.commit()

    yield test

    session.query(UserFeature).delete()
    session.commit()


@pytest.fixture
@pytest.mark.usefixtures('session')
def association_on(session, user):
    test = UserFeature(
        feature_id=1, user_id=user.id, is_enable=True)

    session.add(test)
    session.commit()

    yield test

    session.query(UserFeature).delete()
    session.commit()


@pytest.fixture
def update_dict():
    update = {
        'name': 'test',
        'route': '/route-test',
        'description': 'update',
        'creator': 'test'
    }

    return update


@pytest.fixture
def form_mock():
    form = {
        'feature_id': 1,
        'user_id': 1
    }

    return form


def test_create_features_at_startup(mocker, session, mock_features):

    mocker.patch(
        'app.internal.features.features',
        mock_features
    )
    mocker.patch(
        'app.internal.features.is_feature_exists_in_db',
        return_value=False
    )

    assert internal.create_features_at_startup(session)


def test_create_association(session, user):
    assert internal.create_association(
        db=session, feature_id=1, user_id=user.id, is_enable=False
    ) is not None


def test_get_user_enabled_features(session, feature, association_on):
    assert internal.get_user_enabled_features(session)[0].get(
        'is_enabled') is True


def test_get_user_disabled_features(session, feature, association_off):
    assert internal.get_user_disabled_features(session)[0].get(
        'is_enabled') is False


def test_is_association_exist_in_db(session, form_mock, association_off):
    assert internal.is_association_exists_in_db(form_mock, session)


def test_delete_feature(session, feature):
    feat = session.query(Feature).filter_by(name=feature.name).first()

    internal.delete_feature(feature=feat, session=session)

    feat = session.query(Feature).filter_by(name=feature.name).first()

    assert feat is None


def test_is_feature_exist_in_db(session, feature, update_dict):
    assert internal.is_feature_exists_in_db(update_dict, session)


def test_update_feature(session, feature, update_dict):
    feature = internal.update_feature(feature, update_dict, session)
    assert feature.description == 'update'


def test_is_feature_exist_in_enabled(session, feature, association_on):
    feat = session.query(Feature).filter_by(name=feature.name).first()
    assert internal.is_feature_exists_in_enabled(feat, session)


def test_is_feature_exist_in_disabled(session, feature, association_off):
    feat = session.query(Feature).filter_by(name=feature.name).first()
    assert internal.is_feature_exists_in_disabled(feat, session)


def test_is_feature_enabled(mocker, session, association_on):
    mocker.patch(
        'app.internal.features.SessionLocal',
        return_value=session
    )
    assert internal.is_feature_enabled(route='/route') is True


def test_create_feature(session):

    feat = internal.create_feature(
        name='test1', route='/route', description='testing', creator='test'
    )

    assert feat.name == 'test1'


def test_index(mocker, features_test_client, mock_features):
    url = route.router.url_path_for('index')

    resp = features_test_client.get(url)
    assert resp.ok


def test_add_feature_to_user(features_test_client, feature, form_mock):
    url = route.router.url_path_for('add_feature_to_user')

    resp = features_test_client.post(url, data=form_mock)
    assert resp.ok


def test_delete_user_feature_association(
    features_test_client, form_mock, association_on
):
    url = route.router.url_path_for('delete_user_feature_association')

    resp = features_test_client.post(url, data=form_mock)
    assert resp.ok
    assert resp.content == b'true'


def test_enable_feature(features_test_client, form_mock, association_off):
    url = route.router.url_path_for('enable_feature')

    resp = features_test_client.post(url, data=form_mock)
    assert resp.ok
    assert resp.content == b'true'


def test_disable_feature(features_test_client, form_mock, association_off):
    url = route.router.url_path_for('disable_feature')

    resp = features_test_client.post(url, data=form_mock)
    assert resp.ok
    assert resp.content == b'true'


def test_show_user_enabled_features(mocker, features_test_client):

    mocker.patch(
        'app.routers.features.get_user_enabled_features',
        return_value=True
    )

    url = route.router.url_path_for('show_user_enabled_features')

    resp = features_test_client.get(url)
    assert resp.ok
    assert resp.content == b'true'


def test_show_user_disabled_features(mocker, features_test_client):

    mocker.patch(
        'app.routers.features.get_user_disabled_features',
        return_value=True
    )

    url = route.router.url_path_for('show_user_disabled_features')

    resp = features_test_client.get(url)
    assert resp.ok
    assert resp.content == b'true'


def test_get_user_unlinked_features(mocker, features_test_client, session):
    unlinked = Feature(
        name='unlinked',
        route='/unlinked',
        description='unlinked',
        creator='unlinked',
        icon='unlinked'
    )

    session.add(unlinked)
    session.commit()

    mocker.patch(
        'app.routers.features.is_feature_exists_in_disabled',
        return_value=False
    )
    mocker.patch(
        'app.routers.features.is_feature_exists_in_enabled',
        return_value=False
    )

    url = route.router.url_path_for('get_user_unlinked_features')

    resp = features_test_client.get(url)
    assert resp.ok
    json_resp = resp.json()
    print(json_resp)
    session.query(Feature).delete()
    session.commit()
    assert len(json_resp) == 1
