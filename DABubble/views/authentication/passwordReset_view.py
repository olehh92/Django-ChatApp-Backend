from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from DABubble.models import User
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

class PasswordRequestView(APIView):
    """
    PasswordRequestView handles password reset requests by sending a reset link to the provided email.

    HTTP Methods:
    - POST: Accepts an email address and sends a password reset link if the email is associated with a user account.

    Attributes:
    - permission_classes (list): Allows unauthenticated users to access this endpoint (AllowAny).

    Behavior:
    - Accepts an email address via the POST request.
    - Verifies if a user exists with the provided email.
    - If the user exists, generates a password reset token and constructs a reset link.
    - Sends an email containing the reset link to the provided email address.
    - Returns a success message upon sending the email or an error if the user does not exist.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('emailName')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "User with this email does not exist"}, status=400)

        token = default_token_generator.make_token(user)
        reset_link = f'http://localhost:4200/reset-password?token={token}&uid={user.pk}'

        subject = 'DABubble Password Reset Request'
        html_content = render_to_string('password_reset_email.html', {
            'username': user.username,
            'reset_link': reset_link,
        })

        text_content = strip_tags(html_content)

        send_mail(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=html_content
        )

        return JsonResponse({"message": "Password reset link sent successfully"}, status=200)


class PasswordResetConfirm(APIView):
    """
    PasswordResetConfirm handles confirming a password reset using a token and user ID.

    HTTP Methods:
    - POST: Resets the user's password if the provided token and user ID are valid.

    Behavior:
    - Accepts a password reset token, user ID, and new password via the POST request.
    - Validates the token against the user ID to ensure it is valid and not expired.
    - Updates the user's password if validation is successful.
    - Returns a success message upon successful password reset or an error message if validation fails.
    """
    def post(self, request, *args, **kwargs):
        
        token = request.data.get('token')
        userId = request.data.get('uid')
        new_password = request.data.get('password')
        
        try:
            user = User.objects.get(pk=userId)
        except User.DoesNotExist:
            return Response({"error": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST)
        
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"erorr": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)