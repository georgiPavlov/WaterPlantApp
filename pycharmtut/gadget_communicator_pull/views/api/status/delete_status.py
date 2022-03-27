from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework import status
from rest_framework import status as status_ext

from gadget_communicator_pull.models import Status, Device


class ApiDeleteStatus(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        devices = Device.objects.filter(owner=request.user)
        status_for_user = Status.objects.filter(statuses__in=devices)
        if not status_for_user:
            return JsonResponse(status=status_ext.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                            'message': "No such status for user"})
        status_for_user.get(status_id=id_).delete()
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
