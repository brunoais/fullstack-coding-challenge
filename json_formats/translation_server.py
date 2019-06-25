
from flask_marshmallow import Schema
from marshmallow import fields


class TranslationServer(Schema):
    a = fields.Str()
    b = fields.List(fields.Str)
