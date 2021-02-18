from app.routers.menstrual_predictor import get_all_period_days

from app.internal.utils import get_current_user


class TestMenstrualPredictor:
    PREDICTOR_PREFIX = "/menstrual_predictor"
    ADD_PERIOD_START = "/add-period-start"

    @staticmethod
    def test_menstrual_predictor_page_not_signed_up(
            client, session):
        resp = client.get(TestMenstrualPredictor.PREDICTOR_PREFIX)
        assert resp.ok

    @staticmethod
    def test_menstrual_predictor_sign_up(
            client, module_session):
        resp = client.post(TestMenstrualPredictor.PREDICTOR_PREFIX,
                           json={"avg_period_length": 8,
                                 "last_period_date": "2020-11-07"})
        assert resp.__dict__ == ''
        assert resp.ok
        current_user_id = get_current_user(module_session).id
        resp = client.get(
            TestMenstrualPredictor.PREDICTOR_PREFIX +
            TestMenstrualPredictor.ADD_PERIOD_START + "/2020-12-11")
        period_days = get_all_period_days(module_session, current_user_id)
        assert period_days

    @ staticmethod
    def test_add_period_date(
            client, session
    ):
        resp = client.get(
            TestMenstrualPredictor.PREDICTOR_PREFIX +
            TestMenstrualPredictor.ADD_PERIOD_START + "/2020-12-11")
        assert resp.ok
        
