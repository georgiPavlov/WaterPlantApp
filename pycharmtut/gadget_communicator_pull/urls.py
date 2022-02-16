from django.urls import path
from .views import AddDevice
from .views import ListDevice
from .views import DeviceDeleteView
from .views import GetDeviceView
from .views import AddPlan
from .views import ListPlan

from .views import TimeCreate
from .views import AddPlanTime


app_name = 'gadget_communicator_pull'
urlpatterns = [

    path('create/', AddDevice.as_view(), name='courses-create'),
    path('list/', ListDevice.as_view(), name='courses-list'),
    path('delete/<int:id>', DeviceDeleteView.as_view(), name='courses-delete'),
    path('get/<int:id>', GetDeviceView.as_view(), name='courses-get'),

    path('create_plan/', AddPlan.as_view(), name='plans-create'),
    path('list_plan/', ListPlan.as_view(), name='plan-list'),

    path('create_time/', TimeCreate.as_view(), name='plans-time-create'),
    path('create_time_plan/', AddPlanTime.as_view(), name='plans-time-create'),

]
