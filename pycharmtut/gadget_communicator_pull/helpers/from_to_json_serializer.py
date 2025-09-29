import json as simplejson

from gadget_communicator_pull.water_serializers.constants.water_constants import DEVICE, DEVICES, HAS_BEEN_EXECUTED, IS_RUNNING


def to_json_serializer(serializer):
    return simplejson.loads(simplejson.dumps(serializer.data))


def remove_device_field_from_json(json_obj):
    json_obj.pop(DEVICE, None)
    return json_obj


def remove_has_been_executed_field(json_obj):
    json_obj.pop(HAS_BEEN_EXECUTED, None)
    return json_obj


def remove_is_running_field(json_obj):
    json_obj.pop(IS_RUNNING, None)
    return json_obj


def dump_json(json_string):
    print(f'dump_json func road: {json_string}')
    return simplejson.dumps(json_string)
