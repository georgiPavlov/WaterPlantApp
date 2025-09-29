from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

from gadget_communicator_pull.helpers import time_keeper
from gadget_communicator_pull.models import Device
from .serializers import TokenSerializer, UserSerializer
from .water_email import WaterEmail
import re
import uuid

# JWT token generation


class LoginView(generics.CreateAPIView):
    """
    POST authentication/login/
    """

    # This permission class will over ride the global permission
    # class setting
    permission_classes = (permissions.AllowAny,)

    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # login saves the user’s ID in the session,
            # using Django’s session framework.
            login(request, user)
            serializer = TokenSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": str(RefreshToken.for_user(user).access_token)})
            serializer.is_valid()
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ProfilePasswordChangeView(generics.CreateAPIView):
    """
    POST authentication/login/
    """

    # This permission class will over ride the global permission
    # class setting
    permission_classes = (permissions.AllowAny,)

    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        email_sender = WaterEmail()
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        new_password = request.data.get("new_password", "")
        password_new_repeat = request.data.get("password_new_repeat", "")
        user = authenticate(request, username=username, password=password)
        print(f'username: {username}')
        print(f'password: {password}')
        if not username and not password and not new_password and not password_new_repeat:
            return Response(
                data={
                    "message": "username, password, new_password and password_new_repeat are required to "
                               "change user password"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(new_password) < 10:
            return Response(
                data={
                    "message": "password must be more than 10 characters"
                },
                status=status.HTTP_400_BAD_REQUEST)
        if password == new_password:
            return Response(
                data={
                    "message": "new password must be different than current one"
                },
                status=status.HTTP_400_BAD_REQUEST)
        if new_password != password_new_repeat:
            return Response(
                data={
                    "message": "new password fields must match"
                },
                status=status.HTTP_400_BAD_REQUEST)
        if user is not None:
            # login saves the user’s ID in the session,
            # using Django’s session framework.
            login(request, user)
            serializer = TokenSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": str(RefreshToken.for_user(user).access_token)})
            serializer.is_valid()
            user_ = User.objects.filter(username=username).first()
            email_ = user_.email
            user_.set_password(password_new_repeat)
            user_.save()
            email_message = 'Successfully applied changes in your profile'
            email_subject = 'Profile change'
            email_sender.send_email(email_receiver=email_, subject=email_subject, message=email_message)
            return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class ProfileView(generics.CreateAPIView):
    """
    POST authentication/login/
    """

    # This permission class will over ride the global permission
    # class setting
    permission_classes = (permissions.AllowAny,)

    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        email_sender = WaterEmail()
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email = request.data.get("email", "")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        print(f'username: {username}')
        print(f'password: {password}')
        if not username and not password and not email and not first_name and not last_name:
            return Response(
                data={
                    "message": "username, password, email, first name, last name and password repeat are required to "
                               "register a user "
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not re.fullmatch(regex, email):
            return Response(
                data={
                    "message": "invalid email"
                },
                status=status.HTTP_400_BAD_REQUEST)
        if user is not None:
            # login saves the user’s ID in the session,
            # using Django’s session framework.
            login(request, user)
            serializer = TokenSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": str(RefreshToken.for_user(user).access_token)})
            serializer.is_valid()
            user_ = User.objects.filter(username=username).first()
            print(user_.email)
            user_.first_name = first_name
            user_.last_name = last_name
            user_.username = username
            user_.email = email
            user_.save()
            email_message = 'Successfully applied changes in your profile'
            email_subject = 'Profile change'
            email_sender.send_email(email_receiver=email, subject=email_subject, message=email_message)
            return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class ApiListUsers(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        user = User.objects.filter(username=id_).first()
        if user is None:
            return Response(
                data={
                    "message": "There is no user with the registered username"
                },
                status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data, safe=False)


class HealthCheck(generics.ListAPIView):
    def get_queryset(self):
        return User.objects.all()

    def get(self, request, *args, **kwargs):
        devices = Device.objects.all()
        connected_devices = devices.filter(is_connected=True)
        date_k = time_keeper.TimeKeeper(time_keeper.TimeKeeper.get_current_date())
        for connected_device in connected_devices:
            current_time_minus_delta = date_k.get_current_time_minus_delta_seconds(15)
            device_last_check = connected_device.health_relation.all().first()
            device_last_time_check = date_k.get_time_from_time_string(device_last_check.status_time)
            if device_last_time_check < current_time_minus_delta:
                connected_device.is_connected = False
                connected_device.save()
                self.send_email_to_user(connected_device, f'device: {connected_device.device_id} disconnected', 'Error')
        return Response(
                data={
                    "message": "There is no user with the registered username"
                },
                status=status.HTTP_200_OK)


    def send_email_to_user(self, device, execution_message, execution_status):
        if device.send_email:
            user_ = User.objects.filter(announces=device).first()
            email_ = user_.email
            email_sender = WaterEmail()
            email_message = execution_message
            email_subject = f'Device Operation: {execution_status}'
            email_sender.send_email(email_receiver=email_, subject=email_subject, message=email_message)


class RegisterUsersView(generics.CreateAPIView):
    """
    POST authentication/register/
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email_sender = WaterEmail()
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        username = request.data.get("username", "")
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        password_repeat = request.data.get("password_repeat", "")
        if not username and not password and not email and not first_name and not last_name and not password_repeat:
            return Response(
                data={
                    "message": "username, password, email, first name, last name and password repeat are required to "
                               "register a user "
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(password) < 10:
            return Response(
                data={
                    "message": "password must be more than 10 characters"
                },
                status=status.HTTP_400_BAD_REQUEST)
        if password != password_repeat:
            return Response(
                data={
                    "message": "passwords must match"
                },
                status=status.HTTP_400_BAD_REQUEST)
        if not re.fullmatch(regex, email):
            return Response(
                data={
                    "message": "invalid email"
                },
                status=status.HTTP_400_BAD_REQUEST)
        new_user = User.objects.create_user(
            username=username, password=password, email=email, first_name=first_name, last_name=last_name
        )
        email_message = 'Say hello to your new water.me account'
        email_subject = 'Completed registration'
        email_sender.send_email(email_receiver=email, subject=email_subject, message=email_message)
        return Response(
            data=UserSerializer(new_user).data,
            status=status.HTTP_201_CREATED
        )



class RegisterUsersView(generics.CreateAPIView):
    """
    POST authentication/register/
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email_sender = WaterEmail()
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        username = request.data.get("username", "")
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        password_repeat = request.data.get("password_repeat", "")
        if not username and not password and not email and not first_name and not last_name and not password_repeat:
            return Response(
                data={
                    "message": "username, password, email, first name, last name and password repeat are required to "
                               "register a user "
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(password) < 10:
            return Response(
                data={
                    "message": "password must be more than 10 characters"
                },
                status=status.HTTP_400_BAD_REQUEST)
        if password != password_repeat:
            return Response(
                data={
                    "message": "passwords must match"
                },
                status=status.HTTP_400_BAD_REQUEST)
        if not re.fullmatch(regex, email):
            return Response(
                data={
                    "message": "invalid email"
                },
                status=status.HTTP_400_BAD_REQUEST)
        new_user = User.objects.create_user(
            username=username, password=password, email=email, first_name=first_name, last_name=last_name
        )
        email_message = 'Say hello to your new water.me account'
        email_subject = 'Completed registration'
        email_sender.send_email(email_receiver=email, subject=email_subject, message=email_message)
        return Response(
            data=UserSerializer(new_user).data,
            status=status.HTTP_201_CREATED
        )


class ForgotEmailView(generics.CreateAPIView):
    """
    POST authentication/register/
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email_sender = WaterEmail()
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_ = request.data.get("email", "")
        if not email_:
            return Response(
                data={
                    "message": "email is required to send code"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not re.fullmatch(regex, email_):
            return Response(
                data={
                    "message": "invalid email"
                },
                status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email_).first()
        if user is None:
            return Response(
                data={
                    "message": "There is no user with the registered email"
                },
                status=status.HTTP_400_BAD_REQUEST)
        print(f'user: {user.username} and pass: {user.password}')

        x = str(uuid.uuid4().int)
        user.set_password(x[:10])
        user.save()
        email_message = f'Your temporary password is {x[:10]}'
        email_subject = 'Forgotten password'
        email_sender.send_email(email_receiver=email_, subject=email_subject, message=email_message)
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})


class ApiDeleteUser(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        print(id_)
        users_obj = User.objects.all()
        for ct in User.objects.all():
            ct.delete()
        return JsonResponse(status=status.HTTP_200_OK, data={'status': 'success'})
