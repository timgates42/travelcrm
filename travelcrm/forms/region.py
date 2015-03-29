# -*-coding: utf-8 -*-

import colander

from . import(
    ResourceSchema, 
    BaseForm,
    BaseSearchForm
)
from ..resources.region import RegionResource
from ..models import DBSession
from ..models.region import Region
from ..models.note import Note
from ..models.task import Task
from ..lib.qb.region import RegionQueryBuilder
from ..lib.utils.common_utils import translate as _


@colander.deferred
def name_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        region = (
            DBSession.query(Region).filter(
                Region.name == value,
                Region.country_id == request.params.get('country_id')
            ).first()
        )
        if (
            region
            and str(region.id) != request.params.get('id')
        ):
            raise colander.Invalid(
                node,
                _(u'Region already exists'),
            )
    return colander.All(colander.Length(max=128), validator,)


class _RegionSchema(ResourceSchema):
    country_id = colander.SchemaNode(
        colander.Integer(),
    )
    name = colander.SchemaNode(
        colander.String(),
        validator=name_validator
    )


class RegionForm(BaseForm):
    _schema = _RegionSchema

    def submit(self, region=None):
        context = RegionResource(self.request)
        if not region:
            region = Region(
                resource=context.create_resource()
            )
        else:
            region.resource.notes = []
            region.resource.tasks = []
        region.name = self._controls.get('name')
        region.country_id = self._controls.get('country_id')
        for id in self._controls.get('note_id'):
            note = Note.get(id)
            region.resource.notes.append(note)
        for id in self._controls.get('task_id'):
            task = Task.get(id)
            region.resource.tasks.append(task)
        return region


class RegionSearchForm(BaseSearchForm):
    _qb = RegionQueryBuilder
