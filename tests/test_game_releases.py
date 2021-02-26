from app.internal.game_releases_utils import (
    get_games_data_separated_by_days,
    translate_dby_date_to_ymd,
    translate_ymd_date_to_dby,
)
from app.routers.game_release_dates_service import (
    router as game_release_router,
)
from tests.test_login import test_login_successfull

REGISTER_DETAIL = {
    "username": "correct_user",
    "full_name": "full_name",
    "password": "correct_password",
    "confirm_password": "correct_password",
    "email": "example@email.com",
    "description": "",
}


class TestGameReleases:
    @staticmethod
    def test_subscribe_not_logged(client):
        response = client.post(
            game_release_router.url_path_for("subscribe_game_release_service"),
        )
        assert response.ok

    @staticmethod
    def test_subscribe_logged(session, security_test_client):
        test_login_successfull(session, security_test_client)
        response = security_test_client.post(
            game_release_router.url_path_for("subscribe_game_release_service"),
        )
        assert response.ok

    @staticmethod
    def test_unsubscribe_not_logged(client):
        response = client.post(
            game_release_router.url_path_for("subscribe_game_release_service"),
        )
        assert response.ok
        response = client.post(
            game_release_router.url_path_for(
                "unsubscribe_game_release_service",
            ),
        )
        assert response.ok

    @staticmethod
    def test_unsubscribe_logged(session, security_test_client):
        test_login_successfull(session, security_test_client)

        response = security_test_client.post(
            game_release_router.url_path_for("subscribe_game_release_service"),
        )
        assert response.ok
        response = security_test_client.post(
            game_release_router.url_path_for(
                "unsubscribe_game_release_service",
            ),
        )
        assert response.ok

    @staticmethod
    def test_get_game_releases_month(client):
        response = client.get(
            game_release_router.url_path_for("get_game_releases_month"),
        )
        assert response.ok
        assert b"Prince" in response.content

    @staticmethod
    def test_get_game_releases(client):
        day_1 = "2020-12-10"
        day_2 = "2020-12-20"
        dates = {"from-date": day_1, "to-date": day_2}
        response = client.post(
            game_release_router.url_path_for("fetch_released_games"),
            data=dates,
        )
        assert response.ok
        assert b"Xbox" in response.content

    @staticmethod
    def test_get_games_data_separated_by_days():
        day_1 = "2020-12-10"
        day_2 = "2020-12-20"
        formatted = get_games_data_separated_by_days(day_1, day_2)
        assert isinstance(formatted, dict)
        assert "platforms" in formatted["10-December-2020"][0].keys()

    @staticmethod
    def test_ymd_to_dby():
        ymd_date = "2020-12-12"
        assert translate_ymd_date_to_dby(ymd_date) == "12-December-2020"

    @staticmethod
    def test_dby_to_ymd():
        dby_date = "12-December-2020"
        assert translate_dby_date_to_ymd(dby_date) == "2020-12-12"
