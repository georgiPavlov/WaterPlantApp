from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.models import Device, Status
from gadget_communicator_pull.water_serializers.status_serializer import StatusSerializer
from rest_framework import status as status_ext


class ApiListStatus(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        device = get_object_or_404(Device, device_id=id_)
        owner = request.user
        if device.owner != owner:
            return JsonResponse(status=status_ext.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                            'message': "No such device for user"})

        status = Status.objects.filter(statuses=device)
        serializer = StatusSerializer(status, many=True)
        return JsonResponse(serializer.data, safe=False)
