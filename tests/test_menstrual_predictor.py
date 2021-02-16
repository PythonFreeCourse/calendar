class TestMenstrualPredictor:
    PREDICTOR_PREFIX = "/menstrual_predictor"
    ADD_PERIOD_START = "/add-period-start"

    @staticmethod
    def test_menstrual_predictor_page_not_signed_up(
            client, session):
        resp = client.get(TestMenstrualPredictor.PREDICTOR_PREFIX)
        assert resp.ok

    @staticmethod
    def test_add_period_date(
            client, session
    ):
        resp = client.get(
            TestMenstrualPredictor.PREDICTOR_PREFIX +
            TestMenstrualPredictor.ADD_PERIOD_START + "/2020-12-11")
        assert resp.ok
