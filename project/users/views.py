import logging

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import AuditLog
from core.utils import get_client_ip
from users.serializers import RegisterSerializer


logger = logging.getLogger(__name__)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        request = self.context["request"]

        AuditLog.objects.create(
            user=self.user,
            action=AuditLog.Actions.LOGIN,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )

        logger.info(f"Пользователь |{self.user.client.name, self.user.client.surname}| вошёл в аккаунт")

        return data


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]

            token = RefreshToken(refresh_token)
            token.blacklist()

            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Actions.LOGOUT,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT"),
            )

            logger.info(f"Пользователь |{self.user.client.name, self.user.client.surname}| вышел из аккаунта")

            return Response(
                {"detail": "logout success"},
                status=status.HTTP_205_RESET_CONTENT,
            )

        except Exception:
            return Response(
                {"detail": "invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
