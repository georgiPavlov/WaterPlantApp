from django.urls import path

from gadget_communicator_pull.views.api.camera.delete_photo import ApiDeletePhoto
from gadget_communicator_pull.views.api.camera.download_photo import ApiDownloadPhoto
from gadget_communicator_pull.views.api.camera.get_photo_status import ApiGetPhoto
from gadget_communicator_pull.views.api.camera.list_photos import ApiListPhotos
from gadget_communicator_pull.views.api.camera.take_photo_async import ApiTakePhotoAsync
from gadget_communicator_pull.views.api.camera.test_camera import ApiCreatePhoto
from gadget_communicator_pull.views.api.plan.create_plan import ApiCreatePlan
from gadget_communicator_pull.views.api.plan.delete_plan import ApiDeletePlan
from gadget_communicator_pull.views.api.plan.get_plans_by_name import ApiGetPlansByName
from gadget_communicator_pull.views.api.plan.list_plans import ApiListPlans
from gadget_communicator_pull.views.api.plan.update_plan import ApiUpdatePlan
from gadget_communicator_pull.views.api.status.create_status import ApiCreateStatus
from gadget_communicator_pull.views.api.status.delete_status import ApiDeleteStatus
from gadget_communicator_pull.views.api.status.get_status import ApiGetStatus
from gadget_communicator_pull.views.api.status.list_status import ApiListStatus
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
    path('postPhoto', PostPhoto.as_view(), name='post-photo'),
    path('getPhoto/<str:id>', GetPhoto.as_view(), name='get-photo'),
    path('getWaterLevel', GetWaterLevel.as_view(), name='get-water-level'),

    path('api/create_device', ApiCreateDevice.as_view(), name='api_create_device'),
    path('api/list_devices', ApiListDevices.as_view(), name='api_list_devices'),
    path('api/update_device', ApiUpdateDevice.as_view(), name='api_update_device'),
    path('api/delete_device/<str:id>', ApiDeleteDevice.as_view(), name='api_delete_device'),
    path('api/get_device/<str:id>', ApiGetDevice.as_view(), name='api_get_device'),

    path('api/create_plan', ApiCreatePlan.as_view(), name='api_create_plan'),
    path('api/list_plans', ApiListPlans.as_view(), name='api_list_plans'),
    path('api/get_plans_by_name/<str:id>', ApiGetPlansByName.as_view(), name='api_get_plans_by_device_id'),
    path('api/update_plan', ApiUpdatePlan.as_view(), name='api_update_plan'),
    path('api/delete_plan', ApiDeletePlan.as_view(), name='api_delete_plan'),

    path('api/create_status', ApiCreateStatus.as_view(), name='api_create_status'),
    path('api/list_status/<str:id>', ApiListStatus.as_view(), name='api_list_status'),
    path('api/get_status/<str:id>', ApiGetStatus.as_view(), name='api_get_status'),
    path('api/delete_status/<str:id>', ApiDeleteStatus.as_view(), name='api_delete_status'),

    path('api/test_image/<str:id>', ApiCreatePhoto.as_view(), name='api_create_photo'),

    path('api/photo_operation/device/<str:id_d>', ApiTakePhotoAsync.as_view(), name='api_create_photo'),
    path('api/photo_operation/<str:id>', ApiGetPhoto.as_view(), name='api_get_photo_by_id'),
    path('api/photo_operation/<str:id>/download', ApiDownloadPhoto.as_view(), name='api_download_photo_id'),
    path('api/list_photos/device/<str:id_d>', ApiListPhotos.as_view(), name='api_list_photos'),
    path('api/photo_operation/<str:id>/delete', ApiDeletePhoto.as_view(), name='api_delete_photo_by_id'),

]
