from app.routers.user_exercise import create_user_exercise,\
    does_user_exercise_exist, get_user_exercise
from app.routers.user import create_user


class TestUserExercise:

    def test_create_user_exercise(self, session):
        _user = create_user(
            session=session,
            username='new_test_username',
            password='new_test_password',
            email='new_test.email@gmail.com',
            language='english',
            language_id=1,
        )
        user_exercise = create_user_exercise(
            session=session,
            user=_user
        )
        assert user_exercise.user_id == _user.id
        session.delete(user_exercise)
        session.delete(_user)
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
