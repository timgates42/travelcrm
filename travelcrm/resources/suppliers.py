# -*-coding: utf-8 -*-

from zope.interface import implementer

from ..interfaces import (
    IResourceType,
    ISubaccountFactory,
)
from ..resources import (
    Root,
)
from ..resources import (
    ResourceTypeBase
)
from ..lib.utils.common_utils import translate as _
from ..lib.bl.suppliers import SupplierSubaccountFactory


@implementer(IResourceType)
@implementer(ISubaccountFactory)
class Suppliers(ResourceTypeBase):

    __name__ = 'suppliers'

    def __init__(self, request):
        self.__parent__ = Root(request)
        self.request = request

    @property
    def allowed_permisions(self):
        return [
            ('view', _(u'view')),
            ('add', _(u'add')),
            ('edit', _(u'edit')),
            ('delete', _(u'delete')),
        ]

    @staticmethod
    def get_subaccount_factory():
        return SupplierSubaccountFactory