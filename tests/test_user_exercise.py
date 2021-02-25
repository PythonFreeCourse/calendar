from app.routers.user_exercise import create_user_exercise,\
    does_user_exercise_exist, get_user_exercise
from app.routers.register import _create_user


class TestUserExercise:

    def test_create_user_exercise(self, session):
        user = _create_user(
            session=session,
            username="new_test_username",
            password="new_test_password",
            email="new_test.email@gmail.com",
            language_id=1,
            full_name="test_full_name",
            description="test_description",
        )
        user_exercise = create_user_exercise(
            session=session,
            user=user
        )
        assert user_exercise.user_id == user.id
        session.delete(user_exercise)
        session.delete(user)
        session.commit()

    def test_get_users_exercise_success(self, user_exercise, session):
        assert get_user_exercise(user_id=user_exercise.user_id,
                                 session=session) == [user_exercise]

    def test_get_user_exercise_failure(self, user_exercise, session):
        assert get_user_exercise(user_id=100, session=session) == []

    def test_does_user_exercise_exist_success(self, user_exercise, session):
        assert does_user_exercise_exist(session=session,
                                        user_id=user_exercise.user_id)

    def test_does_user_exercise_exist_failure(self, session):
        assert not does_user_exercise_exist(session=session, user_id=100)
