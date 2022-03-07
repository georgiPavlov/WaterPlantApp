from django.urls import path

from gadget_communicator_pull.views.api.plan.create_plan import ApiCreatePlan
from gadget_communicator_pull.views.api.plan.get_plans_by_device_id import ApiGetPlansByDeviceId
from gadget_communicator_pull.views.api.plan.list_plans import ApiListPlans
from gadget_communicator_pull.views.api.plan.update_plan import ApiUpdatePlan
from gadget_communicator_pull.views.devicecom.device_views import *
from gadget_communicator_pull.views.ui.ui_device_view import *
from gadget_communicator_pull.views.ui.ui_basic_plan_view import *
from gadget_communicator_pull.views.ui.ui_moisture_plan_view import *
from gadget_communicator_pull.views.ui.ui_time_view import *
from gadget_communicator_pull.views.ui.ui_time_plan_view import *
from gadget_communicator_pull.views.api.device.get_device import *
from gadget_communicator_pull.views.api.device.create_device import *
from gadget_communicator_pull.views.api.device.delete_device import *
from gadget_communicator_pull.views.api.device.list_devices import *
from gadget_communicator_pull.views.api.device.update_device import *

app_name = 'gadget_communicator_pull'
urlpatterns = [

    path('create/', AddDevice.as_view(), name='water-create'),
    path('list/', ListDevice.as_view(), name='water-list'),
    path('delete/<int:id>', DeviceDeleteView.as_view(), name='water-delete'),
    path('get/<int:id>', GetDeviceView.as_view(), name='water-get'),

    path('create_plan/', AddPlan.as_view(), name='plans-create'),
    path('list_plan/', ListPlan.as_view(), name='plan-list'),

    path('create_time/', TimeCreate.as_view(), name='plans-time-create'),
    path('create_time_plan/', AddPlanTime.as_view(), name='plans-time-create'),
    path('list_time_plan/', ListTimePlan.as_view(), name='list-time-create'),

    path('create_moisture_plan/', AddMoistureTime.as_view(), name='list-moisture-create'),

    path('getPlan/', GetPlan.as_view(), name='get-plan'),
    path('postWater', PostWater.as_view(), name='post-water'),
    path('postMoisture', PostMoisture.as_view(), name='post-moisture'),
    path('postStatus', PostPlanExecution.as_view(), name='post-execution'),

    path('api/create_device', ApiCreateDevice.as_view(), name='api_create_device'),
    path('api/list_devices', ApiListDevices.as_view(), name='api_list_devices'),
    path('api/update_device', ApiUpdateDevice.as_view(), name='api_update_device'),
    path('api/delete_device/<int:id>', ApiDeleteDevice.as_view(), name='api_delete_device'),
    path('api/get_device/<int:id>', ApiGetDevice.as_view(), name='api_get_device'),

    path('api/create_plan', ApiCreatePlan.as_view(), name='api_create_plan'),
    path('api/list_plans', ApiListPlans.as_view(), name='api_list_plans'),
    path('api/get_plans_by_device_id/<int:id>', ApiGetPlansByDeviceId.as_view(), name='api_get_plans_by_device_id'),
    path('api/update_plan', ApiUpdatePlan.as_view(), name='api_update_plan'),
]
