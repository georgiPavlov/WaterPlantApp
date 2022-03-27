import uuid

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, generics

from gadget_communicator_pull.models import Status, Device
from gadget_communicator_pull.water_serializers.status_serializer import StatusSerializer
from rest_framework import status as status_ext


class ApiGetStatus(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def is_valid_uuid(self, id):
        try:
            uuid.UUID(str(id))
            return True
        except ValueError:
            return False

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        if not self.is_valid_uuid(id_):
            return JsonResponse(status=status_ext.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "uuid is not valid"})
        devices = Device.objects.filter(owner=request.user)
        status_for_user = Status.objects.filter(statuses__in=devices)
        if not status_for_user:
            return JsonResponse(status=status_ext.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                        'message': "No such status for user"})
        status_t = status_for_user.filter(status_id=id_).first()
        if status_t is None:
                return JsonResponse(status=status_ext.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                            'message': "No such status"})
        serializer = StatusSerializer(status_t)
        return JsonResponse(serializer.data)
