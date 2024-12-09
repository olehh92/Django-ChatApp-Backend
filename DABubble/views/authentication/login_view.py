import logging
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from ...serializers import CustomAuthTokenSerializer
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class LoginView(ObtainAuthToken):
    """
    LoginView handles user authentication by validating credentials
    and returning an authentication token.

    HTTP Methods:
    - POST: Validates user credentials and returns a token along with user details.

    Attributes:
    - serializer_class (CustomAuthTokenSerializer): The serializer used to validate user credentials.
    """
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        logger.debug(f'Received data: {request.data}')
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })