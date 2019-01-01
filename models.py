import os
from datetime import datetime

from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy

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

    def save(self):
        db_session.add(self)
        db_session.commit()
        return self


class Item(Base, BaseMixin):
    __tablename__ = 'items'

    url =               Column(String, unique=True)

# Not every scraping project involves searching for keywords,
# but it's a common enough pattern that I figured I'd include
# some generic patterns for how to track search results when
# items may appear for multiple queries (many-to-many relationship)


class Keyword(Base, BaseMixin):
    __tablename__ = 'keywords'

    keyword =           Column(String, unique=True)

    items =             association_proxy("search_results", "item")



class SearchResult(Base, BaseMixin):
    __tablename__ = 'search_results'

    rank =              Column(Integer)
    rank_at =           Column(DateTime)  # should be identifier that is consistent across all items in one scrape

    item_id =           Column(Integer, ForeignKey('items.id'))
    keyword_id =        Column(Integer, ForeignKey('keywords.id'))

    item =              relationship(Item, backref="search_results")
    keyword =           relationship(Keyword, backref="search_results")

    @declared_attr
    def __table_args__(cls):
        return (
            UniqueConstraint('rank', 'rank_at', 'keyword_id', name='unique_rank_per_keyword_per_scrape'),
        )
