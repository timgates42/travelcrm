# -*-coding: utf-8-*-

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref

from ..models import (
    DBSession,
    Base
)


class Service(Base):
    __tablename__ = 'service'
    __table_args__ = (
        UniqueConstraint(
            'name',
            name='unique_idx_name_service',
            use_alter=True,
        ),
    )

    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True
    )
    resource_id = Column(
        Integer,
        ForeignKey(
            'resource.id',
            name="fk_resource_id_service",
            ondelete='restrict',
            onupdate='cascade',
            use_alter=True,
        ),
        nullable=False,
    )
    name = Column(
        String(length=32),
        nullable=False,
    )
    descr = Column(
        String(length=256),
    )
    resource = relationship(
        'Resource',
        backref=backref(
            'service',
            uselist=False,
            cascade="all,delete"
        ),
        cascade="all,delete",
        uselist=False,
    )

    @classmethod
    def get(cls, id):
        if id is None:
            return None
        return DBSession.query(cls).get(id)

    @classmethod
    def by_name(cls, name):
        return DBSession.query(cls).filter(cls.name == name).first()
