"""
API view for listing devices.

This module provides a RESTful API endpoint for retrieving a list of devices
owned by the authenticated user with comprehensive filtering and pagination.
"""
from typing import Dict, Any, List
from django.http import JsonResponse
from django.db.models import QuerySet
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from gadget_communicator_pull.models import Device
from gadget_communicator_pull.water_serializers.device_serializer import DeviceSerializer


class ApiListDevices(generics.ListAPIView):
    """
    API endpoint for listing devices.
    
    Provides a comprehensive list of devices with filtering, searching,
    and ordering capabilities. Only returns devices owned by the
    authenticated user.
    
    Features:
    - User-based filtering (only owned devices)
    - Search by device ID, label, and location
    - Filter by status, connection state, and water levels
    - Ordering by various fields
    - Pagination support
    """
    
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'status': ['exact', 'in'],
        'is_connected': ['exact'],
        'water_level': ['gte', 'lte', 'exact'],
        'moisture_level': ['gte', 'lte', 'exact'],
        'water_container_capacity': ['gte', 'lte', 'exact'],
        'created_at': ['gte', 'lte', 'exact'],
        'updated_at': ['gte', 'lte', 'exact'],
    }
    search_fields = ['device_id', 'label', 'location', 'notes']
    ordering_fields = [
        'device_id', 'label', 'status', 'is_connected', 
        'water_level', 'moisture_level', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self) -> QuerySet[Device]:
        """
        Get queryset filtered by user ownership.
        
        Returns:
            QuerySet[Device]: Devices owned by the authenticated user
        """
        return Device.objects.filter(owner=self.request.user).select_related('owner')

    def get(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle GET request for listing devices.
        
        Args:
            request: HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: JSON response with device data
        """
        try:
            # Get filtered and paginated queryset
            queryset = self.filter_queryset(self.get_queryset())
            
            # Apply pagination if configured
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            # Serialize all results if no pagination
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'success': True,
                'count': queryset.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to retrieve devices',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Get serializer context with request information.
        
        Returns:
            Dict[str, Any]: Serializer context
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }
