from django.urls import path
from .views import AddDevice
from .views import ListDevice
from .views import DeviceDeleteView
from .views import GetDeviceView

app_name = 'gadget_communicator_pull'
urlpatterns = [

    path('create/', AddDevice.as_view(), name='courses-create'),
    path('list/', ListDevice.as_view(), name='courses-list'),
    path('delete/<int:id>', DeviceDeleteView.as_view(), name='courses-delete'),
    path('get/<int:id>', GetDeviceView.as_view(), name='courses-get'),
]
