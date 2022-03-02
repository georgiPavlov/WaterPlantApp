from django.urls import path
from gadget_communicator_pull.views.devicecom.device_views import *
from gadget_communicator_pull.views.ui.ui_device_view import *
from gadget_communicator_pull.views.ui.ui_basic_plan_view import *
from gadget_communicator_pull.views.ui.ui_moisture_plan_view import *
from gadget_communicator_pull.views.ui.ui_time_view import *
from gadget_communicator_pull.views.ui.ui_time_plan_view import *

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
]
