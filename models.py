import os
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

engine = create_engine(os.environ["DATABASE_URL"])
Session = sessionmaker(bind=engine)
db_session = Session()

Base = declarative_base()


class BaseMixin(object):
    # a base class for logic we want to extend into other models
    id =                Column(Integer, primary_key=True)
    created_at =        Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at =        Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        # Convert all the attributes in this instance of a model
        # into a python dict. Useful for JSON serialization.
        cols = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for k, v in cols.items():
            if isinstance(v, datetime.datetime):
                cols[k] = v.isoformat()
            elif isinstance(v, datetime.date):
                cols[k] = v.strftime("%Y-%m-%d")
            elif isinstance(v, datetime.time):
                cols[k] = v.strftime("%H:%M:%S")
        return cols


class Item(Base, BaseMixin):
    __tablename__ = 'items'

    url =               Column(String, unique=True)

