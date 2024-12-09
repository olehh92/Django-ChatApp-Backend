import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class LogoutView(APIView):
    """
    LogoutView handles user logout by deleting the authentication token.

    HTTP Methods:
    - POST: Invalidates the user's session by deleting their authentication token.

    Attributes:
    - authentication_classes (list): Specifies the authentication backend used (TokenAuthentication).
    - permission_classes (list): Ensures that only authenticated users can access this endpoint.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)