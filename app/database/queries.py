from settings.logger import logger

from .database import Session, Subscription, Symbol


def check_symbol(symbol: str):
    session = Session()
    get_symbol = session.query(Symbol).get(symbol)
    if get_symbol:
        return True
    return False


def add_subscription(user_id: int, symbol: str, min: float, max: float):
    session = Session()
    session.begin()
    try:
        new_subsription = Subscription(
            user_id=user_id, symbol=symbol, min_threshold=min, max_threshold=max
        )
        if not check_symbol(symbol):
            new_symbol = Symbol(symbol=symbol)
            session.add(new_symbol)
        session.add(new_subsription)
        session.commit()
        res = True
    except Exception as e:
        logger.error(
            f"Could not create subscription with data: {user_id}, {symbol}, {min}, {max}; {e} "
        )
        res = False
        session.rollback()
    session.close()
    return res


def delete_subscription(id: int):
    session = Session()
    subscription = session.query(Subscription).get(id)
    if subscription:
        session.delete(subscription)
        session.commit()
        res = True
    else:
        res = False
    session.close()
    return res


def get_all_symbols():
    session = Session()
    symbols = (
        session.execute(session.query(Symbol).with_entities(Symbol.symbol))
        .scalars()
        .all()
    )
    session.close()
    return symbols


def get_all_subscriptions():
    session = Session()
    subscriptions = session.query(Subscription).all()
    session.close
    return subscriptions


def get_subscription(id: int):
    session = Session()
    subscription = session.query(Subscription).get(id)
    session.close
    return subscription


def get_user_subscriptions(user_id: int):
    session = Session()
    subscriptions = session.query(Subscription).filter_by(user_id=user_id).all()
    session.close
    return subscriptions
