from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.models import User, UserExercise
from app.internal.utils import save


def create_user_exercise(user: User, session: Session) -> UserExercise:
    """
    Create and save new user exercise
    """
    if not does_user_exercise_exist(session=session, userid=user.id):
        user_exercise = UserExercise(
            user_id=user.id,
            start_date=datetime.now()
            )
        save(user_exercise, session=session)
    else:
        user_exercise = update_user_exercise(user, session)
    return user_exercise


def does_user_exercise_exist(session: Session, userid: int) -> bool:
    """
      Checking if user exercise with user id is exist
    """
    return len(get_user_exercise(session=session, user_id=userid)) == 1


def get_user_exercise(session: Session, **param) -> list:
    """Returns user exercise filter by user id."""

    try:
        exercise = list(session.query(UserExercise).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return exercise


def update_user_exercise(user: User, session: Session) -> UserExercise:
    user_exercise = session.query(UserExercise).filter_by(user_id=user.id).first()
    # Update database
    user_exercise.start_date = datetime.now()
    session.commit()
    return user_exercise
