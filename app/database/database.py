from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///database.db")
Session = sessionmaker(bind=engine)


class Symbol(Base):
    __tablename__ = "crypto_symbol"
    symbol = Column(String, primary_key=True)


class Subscription(Base):
    __tablename__ = "crypto_subscription"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)
    min_threshold = Column(Float, nullable=False)
    max_threshold = Column(Float, nullable=False)


def start_db():
    Base.metadata.create_all(engine)
