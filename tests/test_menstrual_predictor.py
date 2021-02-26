from app.routers.menstrual_predictor import router


class TestMenstrualPredictor:
    @staticmethod
    def test_menstrual_predictor_page_not_signed_up(client, session):
        resp = client.get(router.url_path_for("join_menstrual_predictor"))
        assert resp.ok

    @staticmethod
    def test_menstrual_predictor_sign_up(client, session):
        resp = client.post(
            router.url_path_for("join_menstrual_predictor"),
            json={"avg-period-length": 8, "last-period-date": "2020-11-07"},
        )
        assert resp.ok

        url = router.url_path_for("add_period_start", start_date="2020-12-11")
        resp = client.get(url)

        assert resp.ok

    @staticmethod
    def test_add_period_date(client, session):
        url = router.url_path_for("add_period_start", start_date="2020-12-11")
        resp = client.get(url)
        assert resp.ok
