class TestWeight:
    WEIGHT = "/weight"
    WAY_TO_GO = b'15.5'
    """Target weight set to 60"""

    @staticmethod
    def test_weight_ok(weight_test_client, user, session):
        new_weight = {'target': user.target_weight, 'current_weight': 70}
        resp = weight_test_client.post(TestWeight.WEIGHT, data=new_weight)
        assert resp.ok

    @staticmethod
    def test_need_to_lose_weight(weight_test_client, user):
        new_weight = {'target': user.target_weight, 'current_weight': 80}
        resp = weight_test_client.post(TestWeight.WEIGHT, data=new_weight)
        assert b"Weight to lose" in resp.content

    @staticmethod
    def test_need_to_gain_weight(weight_test_client, user):
        new_weight = {'target': user.target_weight, 'current_weight': 50}
        resp = weight_test_client.post(TestWeight.WEIGHT, data=new_weight)
        assert b"Weight to add" in resp.content

    @staticmethod
    def test_reached_the_goal(weight_test_client, user):
        new_weight = {'target': user.target_weight, 'current_weight': 60}
        resp = weight_test_client.post(TestWeight.WEIGHT, data=new_weight)
        assert b"reached your goal" in resp.content

    @staticmethod
    def test_way_to_go(weight_test_client, user):
        new_weight = {'target': user.target_weight, 'current_weight': 75.5}
        resp = weight_test_client.post(TestWeight.WEIGHT, data=new_weight)
        assert TestWeight.WAY_TO_GO in resp.content

    @staticmethod
    def test_no_target_entered(weight_test_client, user):
        """In this case, the target set to current weight"""

        new_weight = {'target': '', 'current_weight': 60}
        resp = weight_test_client.post(TestWeight.WEIGHT, data=new_weight)
        assert b"reached your goal" in resp.content
