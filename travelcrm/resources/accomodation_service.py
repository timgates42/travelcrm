# -*-coding: utf-8 -*-
from zope.interface import implementer

from ..interfaces import (
    IResourceType,
    IServiceType,
)
from ..resources import (
    ResourceTypeBase,
)


@implementer(IResourceType)
@implementer(IServiceType)
class AccomodationServiceResource(ResourceTypeBase):

    __name__ = 'accomodation_service'
