from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String

from sqlalchemy.orm import relationship
from api.database import Base


class LanguagesORM(Base):
    """Models with languages which available to compare.
    In moment, available: Python, JavaScript, Ruby, PHP, Java"""

    __tablename__ = 'Languages'

    id = Column(Integer, primary_key=True)
    language = Column(String(250), nullable=False)
    r = relationship('StatisticsORM')


class StatisticsORM(Base):
    """Models with vacancies statistics"""

    __tablename__ = 'Statistics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    language_id = Column(Integer, ForeignKey('Languages.id'))
    region_id = Column(Integer, ForeignKey('Regions.id'))
    site_id = Column(Integer, ForeignKey('Sites.id'), default=1)
    vacancies = Column(Integer)
    date = Column(Date)
    no_experience = Column(Integer, default=0)


class RegionsORM(Base):
    """Models with regions ID. The region IDs in the database are the
    same as the region IDs given by the HH API"""

    __tablename__ = 'Regions'

    id = Column(Integer, primary_key=True)
    region = Column(String(255), nullable=False)
    r = relationship('StatisticsORM')


class SitesORM(Base):
    """Recruiting platforms available for parsing jobs. Currently there is
    one platform available - HH.ru"""

    __tablename__ = 'Sites'

    id = Column(Integer, primary_key=True)
    site = Column(String(255))
    r = relationship('StatisticsORM')


class Users(Base):
    """Info about users. This functional are not realized yet"""

    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, default='')
    experience = Column(Boolean, nullable=False)
    employed = Column(Boolean, nullable=False)
    telegram_id = Column(Integer, nullable=False, unique=True)
    description = Column(String, default='', unique=False)
