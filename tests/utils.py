from sqlalchemy.orm import Session


def create_model(session: Session, model_class, **kw):
    instance = model_class(**kw)
    session.add(instance)
    session.commit()
    return instance


def delete_instance(session: Session, instance):
    session.delete(instance)
    session.commit()
