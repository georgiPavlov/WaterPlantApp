from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework import generics
import json

from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.constants.photo_constants import PHOTO_RUNNING, PHOTO_READY, PHOTO_CREATED
from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.photo_module import PhotoModule
from gadget_communicator_pull.water_serializers.base_plan_serializer import BasePlanSerializer
from gadget_communicator_pull.water_serializers.constants.water_constants import DEVICE, WATER_LEVEL, \
    MOISTURE_LEVEL, EXECUTION_STATUS, EXECUTION_MESSAGE, IMAGE

from gadget_communicator_pull.helpers.from_to_json_serializer import to_json_serializer, \
    remove_device_field_from_json
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
        print(type(plan_json))
        json_without_device_field = remove_device_field_from_json(plan_json)
        # plan1 = {"name": "plant1", "plan_type": "time_based", "water_volume": 200,
        #         "water_times": [{"weekday": "Friday", "time_water": "07:47 PM"}]}
        # plan1 = {"name": "plant1", "plan_type": "basic", "water_volume": 200}
        # plan = {"name": "plant1", "plan_type": "moisture", "water_volume": 200, "moisture_threshold": 0.8,
        #  "check_interval": 1}

        return JsonResponse(json_without_device_field, safe=False)


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
        if device_guid is None:
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

        device.status_relation = status_el
        device.save()
        return JsonResponse(body_data)

    class PostPicture(generics.CreateAPIView, DeviceObjectMixin):
        def post(self, request, *args, **kwargs):
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            photo_json = None

            device_guid = body_data[DEVICE]
            if device_guid is None:
                print(f'device_guid {device_guid} is empty')
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)

            device = self.get_device(device_guid)
            if device is None:
                print(f'no such device {device}')
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)
            print(body_data)

            id_ = body_data[IMAGE]
            photo = get_object_or_404(PhotoModule, photo_id=id_)

            if photo_json is None:
                return HttpResponse(status=status.HTTP_204_NO_CONTENT)

            image_file = request.FILES.get('image_file')
            photo.photo_status = PHOTO_READY
            photo.image = image_file
            photo.save()
            print(type(photo_json))
            return JsonResponse(photo_json)

    class GetPhoto(generics.GenericAPIView, DeviceObjectMixin):
        def get(self, request, *args, **kwargs):
            device_guid = self.get_device_guid(self.request.query_params)
            if device_guid is None:
                print(f'device_guid {device_guid} is empty')
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)

            device = self.get_device(device_guid)
            if device is None:
                print(f'no such device {device}')
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)

            photo_json = None
            photo = None

            if device.filtrated_photos:
                print('posting scenario')
                photos = device.filtrated_photos.all()
                filtrated_photos = photos.filter(status=PHOTO_CREATED)
                if filtrated_photos:
                    photo = filtrated_photos.first()
                    serializer = PhotoSerializer(instance=photo)
                    plan_json = to_json_serializer(serializer)

            if plan_json is None:
                return HttpResponse(status=status.HTTP_204_NO_CONTENT)

            photo.photo_status = PHOTO_RUNNING
            photo.save()

            print(type(photo_json))
            json_without_device_field = remove_device_field_from_json(plan_json)
            return JsonResponse(json_without_device_field, safe=False)
