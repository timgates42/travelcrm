# -*-coding: utf-8 -*-

import colander

from . import ResourceSchema


class PositionSchema(ResourceSchema):
    structure_id = colander.SchemaNode(
        colander.Integer(),
    )
    name = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=128)
    )