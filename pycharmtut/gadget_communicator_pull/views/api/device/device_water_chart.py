from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404

from gadget_communicator_pull.helpers.from_to_json_serializer import to_json_serializer, dump_json
from gadget_communicator_pull.models import Device
from gadget_communicator_pull.models.device_module import WaterChart
from gadget_communicator_pull.water_serializers.device_serializer import WaterChartSerializer
from rest_framework import status as status_ext


class ApiDeviceWaterChart(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        device = get_object_or_404(Device, device_id=id_)
        owner = request.user
        if device.owner != owner:
            return JsonResponse(status=status_ext.HTTP_404_NOT_FOUND, data={'status': 'false',
                                                                            'message': "No such device for user"})
        count = WaterChart.objects.filter(device_relation=device).count()
        print(type(count))
        if count < 10:
            size_for_add = 10 - count
            for x in range(size_for_add):
                water_chart_obj = WaterChart(water_chart=100)
                water_chart_obj.save()
                device.water_charts.add(water_chart_obj)
            device.save()
        water_charts = WaterChart.objects.filter(device_relation=device).order_by('-id')[:10]
        water_charts_rev = reversed(water_charts)
        serializer = WaterChartSerializer(water_charts_rev, many=True)
        return JsonResponse(serializer.data,  safe=False)
