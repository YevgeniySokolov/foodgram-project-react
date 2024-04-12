from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from foodgram.constants import FROM_EMAIL
from .models import User


def send_confirmation_code(email, username):
    user = User.objects.get(email=email, username=username)
    user.confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='E-mail confirmation code',
        message=f'Your confirmation code: {user.confirmation_code}',
        from_email=FROM_EMAIL,
        recipient_list=[email]
    )
    user.save()
