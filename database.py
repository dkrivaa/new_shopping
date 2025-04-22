import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os

Base = declarative_base()


class Order(Base):
    """ This is the main shopping table """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    product = Column(String)
    amount = Column(Integer)
    order_date = Column(DateTime)
    active = Column(Boolean)
    ordered_by = Column(String, nullable=True)
    picture = Column(String, nullable=True)


def create_db(db_name) -> None:
    """ This function creates the database if it does not exist """
    if os.path.exists(db_name):
        pass
    else:
        engine = create_engine(f'sqlite:///{db_name}')
        Base.metadata.create_all(engine)
        print(f"Database created at {db_name}")


def active_orders(db_name: str, ) -> list[dict]:
    """ This function returns all active orders """
    engine = create_engine(f'sqlite:///{db_name}')

    Session = sessionmaker(bind=engine)
    session = Session()

    results = []
    try:
        orders = session.query(Order).filter_by(active=True).all()
        for order in orders:
            results.append({
                'id': order.id,
                'product': order.product,
                'amount': order.amount,
                'date': order.order_date,
                'active': order.active,
                'ordered_by': order.ordered_by,
                'picture': order.picture
            })

        session.close()
        return results
    except SQLAlchemyError as e:
        session.rollback()
        print('Something went wrong: ', e)
        session.close()


def all_orders(db_name: str, ) -> list[dict]:
    """ This function returns all orders regardless of status - active / not active"""
    engine = create_engine(f'sqlite:///{db_name}')

    Session = sessionmaker(bind=engine)
    session = Session()

    results = []
    try:
        orders = session.query(Order).all()
        for order in orders:
            results.append({
                'id': order.id,
                'product': order.product,
                'amount': order.amount,
                'date': order.order_date,
                'active': order.active,
                'ordered_by': order.ordered_by,
                'picture': order.picture
            })

        session.close()
        return results
    except SQLAlchemyError as e:
        session.rollback()
        print('Something went wrong: ', e)
        session.close()


def add_order(db_name: str, product: str, amount: int, ordered_by: str = None,
              picture: str = None) -> str:
    """ This function adds a new order to the database """
    engine = create_engine(f'sqlite:///{db_name}')

    Session = sessionmaker(bind=engine)
    session = Session()

    date = datetime.datetime.now()
    new_order = Order(product=product, amount=amount, order_date=date, active=True,
                      ordered_by=ordered_by, picture=picture)

    try:
        session.add(new_order)
        session.commit()
        session.close()
        return 'Order added'
    except SQLAlchemyError as e:
        session.rollback()
        print('Something went wrong: ', e)
        session.close()
        return 'Something went wrong. Please try again'


def change_status(db_name: str, id_num: int) -> str:
    """ This function changes the status - active / not active -  of the order """
    engine = create_engine(f'sqlite:///{db_name}')

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        order = session.query(Order).filter_by(id=id_num).first()
        order.active = not order.active

        session.commit()
        session.close()
        return 'Status of order changed'
    except SQLAlchemyError as e:
        session.rollback()
        print('Something went wrong: ', e)
        session.close()
        return 'Something went wrong. Please try again'


def change_amount(db_name: str, id_num: int, new_amount: int) -> None:
    """ This function changes the amount of the order """
    engine = create_engine(f'sqlite:///{db_name}')

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        order = session.query(Order).filter_by(id=id_num).first()
        order.amount = new_amount

        session.commit()
        session.close()
    except SQLAlchemyError as e:
        session.rollback()
        session.close()


