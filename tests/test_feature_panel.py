import pytest

from app.database.models import Feature, UserFeature
import app.internal.features as internal
import app.routers.features as route


@pytest.fixture
def mock_features():
    return [
        {
            "name": "test",
            "route": "/test",
            "description": "testing",
            "creator": "test",
        },
    ]


@pytest.fixture
@pytest.mark.usefixtures("session")
def feature(session):
    test = Feature(
        name="test",
        route="/test",
        description="testing",
        creator="test",
    )

    session.add(test)
    session.commit()

    yield test

    session.query(Feature).delete()
    session.commit()


@pytest.fixture
@pytest.mark.usefixtures("session")
def association_off(session, user):
    test = UserFeature(feature_id=1, user_id=user.id, is_enable=False)

    session.add(test)
    session.commit()

    yield test

    session.query(UserFeature).delete()
    session.commit()


@pytest.fixture
@pytest.mark.usefixtures("session")
def association_on(session, user):
    test = UserFeature(feature_id=1, user_id=user.id, is_enable=True)

    session.add(test)
    session.commit()

    yield test

    session.query(UserFeature).delete()
    session.commit()


@pytest.fixture
def update_dict():
    update = {
        "name": "test",
        "route": "/route-test",
        "description": "update",
        "creator": "test",
    }

    return update


@pytest.fixture
def form_mock():
    form = {"feature_id": 1, "user_id": 1}

    return form


def test_create_features_at_startup(mocker, session, mock_features):

    mocker.patch("app.internal.features.features", mock_features)
    mocker.patch("app.internal.features.is_feature_exists", return_value=False)

    assert internal.create_features_at_startup(session)


def test_create_association(mocker, session, user, feature):
    assert (
        internal.create_user_feature_association(
            db=session,
            feature_id=1,
            user_id=user.id,
            is_enable=False,
        )
        is not None
    )


def test_get_user_enabled_features(session, feature, association_on, user):
    assert (
        internal.get_user_enabled_features(session=session, user_id=user.id)[0]
        is not None
    )


def test_is_association_exist_in_db(session, form_mock, association_off, user):
    assert internal.is_association_exists_in_db(form_mock, session, user)


def test_delete_feature(session, feature):
    feat = session.query(Feature).filter_by(name=feature.name).first()
    internal.delete_feature(feature=feat, session=session)
    feat = session.query(Feature).filter_by(name=feature.name).first()
    assert feat is None


def test_is_feature_exist_in_db(session, feature, update_dict):
    assert internal.is_feature_exists(update_dict, session)


def test_update_feature(session, feature, update_dict):
    feature = internal.update_feature(feature, update_dict, session)
    assert feature.description == "update"


def test_is_feature_exist_in_enabled(
    mocker,
    session,
    feature,
    association_on,
    user,
):
    feat = session.query(Feature).filter_by(name=feature.name).first()

    mocker.patch(
        "app.internal.features.get_user_enabled_features",
        return_value=[feat],
    )

    assert internal.is_feature_enabled(user, feat, session)


@pytest.mark.asyncio
async def test_is_feature_enabled(mocker, session, association_on, user):
    mocker.patch("app.internal.features.SessionLocal", return_value=session)
    mocker.patch(
        "app.internal.features.get_authorization_cookie",
        return_value=None,
    )
    mocker.patch(
        "app.internal.features.current_user_from_db",
        return_value=user,
    )

    assert (
        await internal.is_access_allowd(route="/route", request=None) is True
    )


def test_create_feature(session):
    feat = internal.create_feature(
        name="test1",
        route="/route",
        description="testing",
        creator="test",
    )
    assert feat.name == "test1"


def test_index(mocker, features_test_client, mock_features):
    url = route.router.url_path_for("index")

    resp = features_test_client.get(url)
    assert resp.ok


def test_add_feature_to_user(features_test_client, feature, form_mock):
    url = route.router.url_path_for("add_feature_to_user")

    resp = features_test_client.post(url, data=form_mock)
    assert resp.ok


def test_delete_user_feature_association(
    mocker,
    features_test_client,
    form_mock,
    association_on,
    feature,
):
    url = route.router.url_path_for("delete_user_feature_association")

    resp = features_test_client.post(url, data=form_mock)
    assert resp.ok
