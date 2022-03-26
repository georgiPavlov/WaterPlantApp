from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework import generics
import json

from rest_framework.generics import get_object_or_404
from gadget_communicator_pull.constants.photo_constants import PHOTO_RUNNING, PHOTO_READY, PHOTO_CREATED
from gadget_communicator_pull.constants.water_constants import DEVICE_ID, PHOTO_ID, IMAGE_FILE, WATER_PLAN_MOISTURE, \
    WATER_PLAN_TIME, DELETE_RUNNING_PLAN
from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer
from gadget_communicator_pull.water_serializers.constants.water_constants import DEVICE, WATER_LEVEL, \
    MOISTURE_LEVEL, EXECUTION_STATUS, EXECUTION_MESSAGE, IS_RUNNING

from gadget_communicator_pull.helpers.from_to_json_serializer import to_json_serializer, \
    remove_device_field_from_json, remove_has_been_executed_field, remove_is_running_field
from gadget_communicator_pull.water_serializers.moisture_plan_serializer import MoisturePlanSerializer
from gadget_communicator_pull.water_serializers.photo_serializer import PhotoSerializer
from gadget_communicator_pull.water_serializers.status_serializer import StatusSerializer
from gadget_communicator_pull.water_serializers.time_plan_serializer import TimePlanSerializer


class DeviceObjectMixin(object):
    def get_device_guid(self, query_params):
        device_guid = None
        if DEVICE in query_params:
            print(f'{DEVICE} param specified')
            for param in query_params:
                print(f'param:  {param}')
            device_guid = query_params.get(DEVICE)
            print(f'device_guid:  {device_guid}')
        else:
            print(f'{DEVICE} param not specified')
            return None
        return device_guid

    def get_device(self, device_guid):
        return Device.objects.filter(device_id=device_guid).first()


class GetPlan(generics.GenericAPIView, DeviceObjectMixin):
    def get(self, request, *args, **kwargs):
        # plan = {"name": "plant1", "plan_type": "moisture", "water_volume": 200, "moisture_threshold": 0.8,
        #  "check_interval": 1}

        device_guid = self.get_device_guid(self.request.query_params)
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        device = self.get_device(device_guid)
        if device is None:
            print(f'no such device {device}')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        plan_json = None
        plan = None

        if device.device_relation_b:
            print('Basic plan scenario')
            plans = device.device_relation_b.all()
            filtrated_plans = plans.filter(has_been_executed=False)
            if filtrated_plans:
                plan = filtrated_plans.first()
                serializer = BasePlanSerializer(instance=plan)
                plan_json = to_json_serializer(serializer)
        if device.device_relation_m:
            print('Moisture plan scenario')
            plans = device.device_relation_m.all()
            filtrated_plans = plans.filter(has_been_executed=False)
            if filtrated_plans:
                plan = filtrated_plans.first()
                serializer = MoisturePlanSerializer(instance=plan)
                plan_json = to_json_serializer(serializer)
        if device.device_relation_t:
            print('Time plan scenario')
            plans = device.device_relation_t.all()
            filtrated_plans = plans.filter(has_been_executed=False)
            if filtrated_plans:
                plan = filtrated_plans.first()
                serializer = TimePlanSerializer(instance=plan)
                plan_json = to_json_serializer(serializer)

        if plan_json is None:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
        plan.has_been_executed = True
        plan.save()
        if plan.plan_type == WATER_PLAN_MOISTURE or plan.plan_type == WATER_PLAN_TIME \
                or plan.plan_type == DELETE_RUNNING_PLAN:
            self.set_is_running_plan_to_false(device)
            if plan.plan_type == WATER_PLAN_MOISTURE or plan.plan_type == WATER_PLAN_TIME:
                plan.is_running = True
                plan.save()
            plan_json = remove_is_running_field(json_obj=plan_json)
        print(type(plan_json))
        json_without_device_field = remove_device_field_from_json(plan_json)
        final_json = remove_has_been_executed_field(json_without_device_field)
        return JsonResponse(final_json, safe=False)

    def set_is_running_plan_to_false(self, device):
        print('setting devices running flag to false')
        if device.device_relation_m:
            print('is_running to false MOISTURE PLAN')
            plans = device.device_relation_m.all()
            for plan in plans:
                plan.is_running = False
                plan.save(update_fields=[IS_RUNNING])
        if device.device_relation_t:
            print('is_running to false TIME PLAN')
            plans = device.device_relation_t.all()
            for plan in plans:
                plan.is_running = False
                plan.save(update_fields=[IS_RUNNING])


class PostWater(generics.CreateAPIView, DeviceObjectMixin):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        device_guid = body_data[DEVICE]
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        device = self.get_device(device_guid)
        if device is None:
            print(f'no such device {device}')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        print(body_data)

        device_guid = body_data[DEVICE]
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        water_level = body_data[WATER_LEVEL]
        if device_guid is None:
            print(f'water_level {water_level} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        device.water_level = water_level
        device.save()

        return JsonResponse(body_data)


class PostMoisture(generics.CreateAPIView, DeviceObjectMixin):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        device_guid = body_data[DEVICE]
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        device = self.get_device(device_guid)
        if device is None:
            print(f'no such device {device}')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        print(body_data)

        moisture_level = body_data[MOISTURE_LEVEL]
        if device_guid is None:
            print(f'moisture_level {moisture_level} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        device.moisture_level = moisture_level
        device.save()

        return JsonResponse(body_data)


class PostPlanExecution(generics.CreateAPIView, DeviceObjectMixin):
    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        device_guid = body_data[DEVICE]
        if device_guid is None:
            print(f'device_guid {device_guid} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        device = self.get_device(device_guid)
        if device is None:
            print(f'no such device {device}')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        print(body_data)

        execution_status = body_data[EXECUTION_STATUS]
        if execution_status is None:
            print(f'execution_status {execution_status} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        execution_message = body_data[EXECUTION_MESSAGE]
        if device_guid is None:
            print(f'execution_message {execution_message} is empty')
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        print(body_data)
        serializer = StatusSerializer(data=body_data)
        serializer.is_valid()
        status_el = serializer.save()
        print(type(status_el))

        device.status_relation.add(status_el)
        device.save()
        return JsonResponse(body_data)


class PostPhoto(generics.CreateAPIView, DeviceObjectMixin):
    def post(self, request, *args, **kwargs):
        id_d = request.POST.get(DEVICE_ID, None)
        print(f'id_d {id_d}')
        device = get_object_or_404(Device, device_id=id_d)

        id_ = request.POST.get(PHOTO_ID, None)
        print(f'id {id_}')
        photos = device.photo_relation.all()
        photo = photos.filter(photo_id=id_).first()

        if photo is None:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        image_file = request.FILES.get(IMAGE_FILE)
        photo.photo_status = PHOTO_READY
        photo.image = image_file
        photo.save()

        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})


class GetPhoto(generics.GenericAPIView, DeviceObjectMixin):
    def get(self, request, *args, **kwargs):
        device_guid = self.get_device_guid(self.request.query_params)
        device = get_object_or_404(Device, device_id=device_guid)
        photo_json = None
        photo = None
        if device.photo_relation:
            print('posting scenario')
            photos = device.photo_relation.all()
            filtrated_photos = photos.filter(photo_status=PHOTO_CREATED)
            if filtrated_photos:
                photo = filtrated_photos.first()
                serializer = PhotoSerializer(instance=photo)
                photo_json = to_json_serializer(serializer)
        if photo_json is None:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
        photo.photo_status = PHOTO_RUNNING
        photo.save()
        print(type(photo_json))
        json_without_device_field = remove_device_field_from_json(photo_json)
        return JsonResponse(json_without_device_field, safe=False)


class GetWaterLevel(generics.GenericAPIView, DeviceObjectMixin):
    def get(self, request, *args, **kwargs):
        device_guid = self.get_device_guid(self.request.query_params)
        device = get_object_or_404(Device, device_id=device_guid)

        if device.water_reset:
            print(f'update water for {device.device_id}')
            device.water_reset = False
            device.save()
            JsonResponse(status=status.HTTP_200_OK, data={'water': device.water_container_capacity})
        print(f'device water container is not for update {device.device_id}')
        return JsonResponse(status=status.HTTP_204_NO_CONTENT, data={})
