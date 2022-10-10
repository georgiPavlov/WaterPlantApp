from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status as status_ext


class HealthStatus(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        return JsonResponse(status=status_ext.HTTP_200_OK, data={'status': 'success'})
