# -*-coding: utf-8-*-

import logging
import colander

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from ..models import DBSession
from ..models.contact import Contact
from ..lib.qb.contact import ContactQueryBuilder
from ..lib.utils.common_utils import translate as _

from ..forms.contact import ContactSchema


log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.contact.ContactResource',
)
class ContactView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        request_method='GET',
        renderer='travelcrm:templates/contacts/index.mak',
        permission='view'
    )
    def index(self):
        return {}

    @view_config(
        name='list',
        xhr='True',
        request_method='POST',
        renderer='json',
        permission='view'
    )
    def _list(self):
        qb = ContactQueryBuilder(self.context)
        qb.search_simple(
            self.request.params.get('q')
        )
        id = self.request.params.get('id')
        if id:
            qb.filter_id(id.split(','))
        qb.sort_query(
            self.request.params.get('sort'),
            self.request.params.get('order', 'asc')
        )
        qb.page_query(
            int(self.request.params.get('rows')),
            int(self.request.params.get('page'))
        )
        return {
            'total': qb.get_count(),
            'rows': qb.get_serialized()
        }

    @view_config(
        name='view',
        request_method='GET',
        renderer='travelcrm:templates/contacts/form.mak',
        permission='view'
    )
    def view(self):
        if self.request.params.get('rid'):
            resource_id = self.request.params.get('rid')
            contact = Contact.by_resource_id(resource_id)
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'view', query={'id': contact.id}
                )
            )
        result = self.edit()
        result.update({
            'title': _(u"View Contact"),
            'readonly': True,
        })
        return result

    @view_config(
        name='add',
        request_method='GET',
        renderer='travelcrm:templates/contacts/form.mak',
        permission='add'
    )
    def add(self):
        return {
            'title': _(u'Add Contact'),
        }

    @view_config(
        name='add',
        request_method='POST',
        renderer='json',
        permission='add'
    )
    def _add(self):
        schema = ContactSchema().bind(request=self.request)

        try:
            controls = schema.deserialize(self.request.params)
            contact = Contact(
                contact_type=controls.get('contact_type'),
                contact=controls.get('contact'),
                resource=self.context.create_resource()
            )
            DBSession.add(contact)
            DBSession.flush()
            return {
                'success_message': _(u'Saved'),
                'response': contact.id
            }
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }

    @view_config(
        name='edit',
        request_method='GET',
        renderer='travelcrm:templates/contacts/form.mak',
        permission='edit'
    )
    def edit(self):
        contact = Contact.get(self.request.params.get('id'))
        return {
            'item': contact,
            'title': _(u'Edit Contact'),
        }

    @view_config(
        name='edit',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _edit(self):
        schema = ContactSchema().bind(request=self.request)
        contact = Contact.get(self.request.params.get('id'))
        try:
            controls = schema.deserialize(self.request.params)
            contact.contact_type = controls.get('contact_type')
            contact.contact = controls.get('contact')
            return {
                'success_message': _(u'Saved'),
                'response': contact.id
            }
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }

    @view_config(
        name='copy',
        request_method='GET',
        renderer='travelcrm:templates/contacts/form.mak',
        permission='add'
    )
    def copy(self):
        contact = Contact.get(self.request.params.get('id'))
        return {
            'item': contact,
            'title': _(u"Copy Contact")
        }

    @view_config(
        name='copy',
        request_method='POST',
        renderer='json',
        permission='add'
    )
    def _copy(self):
        return self._add()

    @view_config(
        name='delete',
        request_method='GET',
        renderer='travelcrm:templates/contacts/delete.mak',
        permission='delete'
    )
    def delete(self):
        return {
            'title': _(u'Delete Contacts'),
            'id': self.request.params.get('id')
        }

    @view_config(
        name='delete',
        request_method='POST',
        renderer='json',
        permission='delete'
    )
    def _delete(self):
        errors = 0
        for id in self.request.params.getall('id'):
            item = Contact.get(id)
            if item:
                DBSession.begin_nested()
                try:
                    DBSession.delete(item)
                    DBSession.commit()
                except:
                    errors += 1
                    DBSession.rollback()
        if errors > 0:
            return {
                'error_message': _(
                    u'Some objects could not be delete'
                ),
            }
        return {'success_message': _(u'Deleted')}