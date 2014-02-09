# -*-coding: utf-8 -*-

from ..models import (
    DBSession,
    Base
)

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref


class Attachment(Base):
    __tablename__ = 'attachment'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    resource_id = Column(
        Integer,
        ForeignKey(
            'resource.id',
            name="fk_resources_id_attachment",
            ondelete='cascade',
            onupdate='cascade',
            use_alter=True,
        ),
        nullable=False,
    )

    resource = relationship(
        'Resource',
        backref=backref('attachment', uselist=False, cascade="all,delete"),
        cascade="all,delete",
        uselist=False
    )

    @classmethod
    def get(cls, id):
        return DBSession.query(cls).get(id)
