import json as simplejson
from django.core import serializers


def to_json_serializer(serializer):
    return simplejson.loads(simplejson.dumps(serializer.data))
