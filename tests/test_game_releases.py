from app.internal.game_releases_utils import (
    get_games_data_separated_by_days,
    translate_ymd_date_to_dby,
    translate_dby_date_to_ymd,
)


class TestGameReleases:
    @staticmethod
    def test_get_subscribe(client):
        response = client.get("/game-releases/subscribe")
        assert response.ok
        assert b"Profile" in response.content

    @staticmethod
    def test_get_unsubscribe(client):
        response = client.get("/game-releases/subscribe")
        assert response.ok
        response = client.get("/game-releases/unsubscribe")
        assert response.ok
        assert b"Profile" in response.content

    @staticmethod
    def test_get_game_releases_month(client):
        response = client.get(
            "/game-releases/get_game_releases_next_month",
        )
        assert response.ok
        assert b"Prince" in response.content

    @staticmethod
    def test_get_game_releases(client):
        day_1 = "2020-12-10"
        day_2 = "2020-12-20"
        dates = {"from-date": day_1, "to-date": day_2}
        response = client.post(
            "/game-releases/get_releases_by_dates",
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
