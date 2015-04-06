# -*-coding: utf-8-*-

import logging

import colander
from datetime import timedelta
from babel.numbers import format_decimal

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from ..models import DBSession
from ..models.invoice import Invoice
from ..models.resource import Resource
from ..models.account import Account
from ..models.note import Note
from ..models.task import Task
from ..lib.qb import query_serialize
from ..lib.qb.invoice import InvoiceQueryBuilder
from ..lib.utils.common_utils import translate as _
from ..lib.utils.common_utils import format_date

from ..forms.invoice import (
    InvoiceAddSchema,
    InvoiceEditSchema,
    InvoiceSumSchema,
    InvoiceActiveUntilSchema,
    InvoiceSearchSchema,
    SettingsSchema,
)

from ..lib.utils.resources_utils import (
    get_resource_class,
    get_resource_type_by_resource
)
from ..lib.utils.common_utils import get_locale_name
from ..lib.bl.invoices import (
    query_resource_data,
    query_invoice_payments,
)
from ..lib.bl.invoices import get_factory_by_invoice_id

log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.invoice.InvoiceResource',
)
class InvoiceView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        request_method='GET',
        renderer='travelcrm:templates/invoices/index.mak',
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
    def list(self):
        schema = InvoiceSearchSchema().bind(request=self.request)
        controls = schema.deserialize(self.request.params.mixed())
        qb = InvoiceQueryBuilder(self.context)
        qb.search_simple(controls.get('q'))
        qb.advanced_search(**controls)
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
        renderer='travelcrm:templates/invoices/form.mak',
        permission='view'
    )
    def view(self):
        if self.request.params.get('rid'):
            resource_id = self.request.params.get('rid')
            invoice = Invoice.by_resource_id(resource_id)
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'view', query={'id': invoice.id}
                )
            )
        result = self.edit()
        result.update({
            'title': _(u"View Invoice"),
            'readonly': True,
        })
        return result

    @view_config(
        name='add',
        request_method='GET',
        renderer='travelcrm:templates/invoices/form.mak',
        permission='add'
    )
    def add(self):
        resource_id = self.request.params.get('resource_id')
        resource = Resource.get(resource_id)
        source_cls = get_resource_class(resource.resource_type.name)
        factory = source_cls.get_invoice_factory()
        invoice = factory.get_invoice(resource_id)
        if invoice:
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'edit', query={'id': invoice.id}
                ),
            )
        return {
            'title': _(u'Add Invoice'),
            'resource_id': resource_id,
        }

    @view_config(
        name='add',
        request_method='POST',
        renderer='json',
        permission='add'
    )
    def _add(self):
        schema = InvoiceAddSchema().bind(request=self.request)

        try:
            controls = schema.deserialize(self.request.params.mixed())
            resource_id = controls.get('resource_id')
            resource = Resource.get(resource_id)
            source_cls = get_resource_class(resource.resource_type.name)
            factory = source_cls.get_invoice_factory()
            invoice = Invoice(
                date=controls.get('date'),
                active_until=controls.get('active_until'),
                account_id=controls.get('account_id'),
                resource=self.context.create_resource()
            )
            for id in controls.get('note_id'):
                note = Note.get(id)
                invoice.resource.notes.append(note)
            for id in controls.get('task_id'):
                task = Task.get(id)
                invoice.resource.tasks.append(task)
            source = factory.bind_invoice(resource_id, invoice)
            DBSession.add(source)
            DBSession.flush()
            return {
                'success_message': _(u'Saved'),
                'response': invoice.id
            }
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }

    @view_config(
        name='edit',
        request_method='GET',
        renderer='travelcrm:templates/invoices/form.mak',
        permission='edit'
    )
    def edit(self):
        invoice = Invoice.get(self.request.params.get('id'))
        bound_resource = (
            query_resource_data()
            .filter(Invoice.id == invoice.id)
            .first()
        )
        return {
            'item': invoice,
            'resource_id': bound_resource.resource_id,
            'title': _(u'Edit Invoice')
        }

    @view_config(
        name='edit',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _edit(self):
        schema = InvoiceEditSchema().bind(request=self.request)
        invoice = Invoice.get(self.request.params.get('id'))
        try:
            controls = schema.deserialize(self.request.params.mixed())
            invoice.date = controls.get('date')
            invoice.active_until = controls.get('active_until')
            invoice.account_id = controls.get('account_id')
            invoice.resource.notes = []
            invoice.resource.tasks = []
            for id in controls.get('note_id'):
                note = Note.get(id)
                invoice.resource.notes.append(note)
            for id in controls.get('task_id'):
                task = Task.get(id)
                invoice.resource.tasks.append(task)
            return {
                'success_message': _(u'Saved'),
                'response': invoice.id
            }
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }

    @view_config(
        name='delete',
        request_method='GET',
        renderer='travelcrm:templates/invoices/delete.mak',
        permission='delete'
    )
    def delete(self):
        return {
            'title': _(u'Delete Invoices'),
            'rid': self.request.params.get('rid')
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
            item = Invoice.get(id)
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

    @view_config(
        name='print',
        request_method='GET',
        renderer='travelcrm:templates/invoices/print.mak',
        permission='view',
    )
    def print_invoice(self):
        invoice = Invoice.get(self.request.params.get('id'))
        factory = get_factory_by_invoice_id(invoice.id)
        bound_resource = (
            query_resource_data()
            .filter(Invoice.id == invoice.id)
            .first()
        )
        payment_query = query_invoice_payments(self.request.params.get('id'))
        payment_sum = sum(row.sum for row in payment_query)
        return {
            'invoice': invoice,
            'factory': factory,
            'resource_id': bound_resource.resource_id,
            'payment_sum': payment_sum,
        }

    @view_config(
        name='invoice_sum',
        request_method='POST',
        renderer='json',
        permission='view'
    )
    def invoice_sum(self):
        schema = InvoiceSumSchema().bind(request=self.request)
        try:
            controls = schema.deserialize(self.request.params)
            resource_id = controls.get('resource_id')
            account_id = controls.get('account_id')
            date = controls.get('date')
            resource = Resource.get(resource_id)
            source_cls = get_resource_class(resource.resource_type.name)
            factory = source_cls.get_invoice_factory()
            account = Account.get(account_id)
            return {
                'invoice_sum': str(
                    factory.get_sum_by_resource_id(
                        resource.id, account.currency_id, date
                    )
                ),
                'currency': account.currency.iso_code
            }
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }

    @view_config(
        name='invoice_active_until',
        request_method='POST',
        renderer='json',
        permission='view'
    )
    def invoice_active_until(self):
        schema = InvoiceActiveUntilSchema().bind(request=self.request)
        try:
            controls = schema.deserialize(self.request.params)
            date = controls.get('date')
            rt = get_resource_type_by_resource(self.context)
            active_days = rt.settings.get('active_days', 0)
            return {
                'active_until': format_date(
                    date + timedelta(days=active_days)
                )
            }
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }

    @view_config(
        name='info',
        request_method='GET',
        renderer='travelcrm:templates/invoices/info.mak',
        permission='view'
    )
    def info(self):
        invoice = Invoice.get(self.request.params.get('id'))
        return {
            'title': _(u'Invoice Info'),
            'currency': invoice.account.currency.iso_code,
            'id': invoice.id
        }

    @view_config(
        name='services_info',
        request_method='POST',
        renderer='json',
        permission='view'
    )
    def _services_info(self):
        invoice = Invoice.get(self.request.params.get('id'))
        bound_resource = (
            query_resource_data()
            .filter(Invoice.id == invoice.id)
            .first()
        )
        resource = Resource.get(bound_resource.resource_id)
        source_cls = get_resource_class(resource.resource_type.name)
        factory = source_cls.get_invoice_factory()
        query = factory.services_info(
            bound_resource.resource_id, invoice.account.currency.id
        )
        total_cnt = sum(row.cnt for row in query)
        total_sum = sum(row.price for row in query)
        return {
            'rows': query_serialize(query),
            'footer': [{
                'name': _(u'total'),
                'cnt': total_cnt,
                'price': format_decimal(total_sum, locale=get_locale_name())
            }]
        }

    @view_config(
        name='accounts_items_info',
        request_method='POST',
        renderer='json',
        permission='view'
    )
    def _accounts_items_info(self):
        invoice = Invoice.get(self.request.params.get('id'))
        bound_resource = (
            query_resource_data()
            .filter(Invoice.id == invoice.id)
            .first()
        )
        resource = Resource.get(bound_resource.resource_id)
        source_cls = get_resource_class(resource.resource_type.name)
        factory = source_cls.get_invoice_factory()
        query = factory.accounts_items_info(
            bound_resource.resource_id, invoice.account.currency.id
        )
        total_cnt = sum(row.cnt for row in query)
        total_sum = sum(row.price for row in query)
        return {
            'rows': query_serialize(query),
            'footer': [{
                'name': _(u'total'),
                'unit_price': None,
                'cnt': total_cnt,
                'price': format_decimal(total_sum, locale=get_locale_name()),
            }]
        }

    @view_config(
        name='payments_info',
        request_method='POST',
        renderer='json',
        permission='view'
    )
    def _payments_info(self):
        query = query_invoice_payments(self.request.params.get('id'))
        total_sum = sum(row.sum for row in query)
        return {
            'rows': query_serialize(query),
            'footer': [{
                'date': _(u'total'),
                'sum': format_decimal(total_sum, locale=get_locale_name())
            }]
        }

    @view_config(
        name='settings',
        request_method='GET',
        renderer='travelcrm:templates/invoices/settings.mak',
        permission='settings',
    )
    def settings(self):
        rt = get_resource_type_by_resource(self.context)
        return {
            'title': _(u'Settings'),
            'rt': rt,
        }

    @view_config(
        name='settings',
        request_method='POST',
        renderer='json',
        permission='settings',
    )
    def _settings(self):
        schema = SettingsSchema().bind(request=self.request)
        try:
            controls = schema.deserialize(self.request.params)
            rt = get_resource_type_by_resource(self.context)
            rt.settings = {'active_days': controls.get('active_days')}
            return {'success_message': _(u'Saved')}
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }