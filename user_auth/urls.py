from django.urls import path, re_path
from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView, LoginView, LogoutView, UserDetailsView, \
    PasswordChangeView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def rest_auth_root(request, format=None):
    return Response({
        'login': reverse('rest_login', request=request, format=format),
        'logout': reverse('rest_logout', request=request, format=format),
        'me': reverse('rest_user_details', request=request, format=format),
        'password change': reverse('rest_password_change', request=request, format=format),
        'password reset': reverse('rest_password_reset', request=request, format=format),
        'password reset confirm': reverse('rest_password_reset_confirm', request=request, format=format),
        'registration': reverse('rest_register', request=request, format=format),
        'registration verify-email': reverse('account_email_verification_sent', request=request, format=format),
    })


# original patterns from dj_rest_auth
# ---- Notice 1
# the re_path registration/verify_email/(?...) url is needed to generate the activation_url
# should be removed in live and the activation_url needs to be replaced with the url of the website.
# the related template is in account/email/email_confirmation_message.txt
# ---- Notice 2
# also the link in the registration/password_reset_email.html needs to be changed in live.
# ---- Notice 3
# if you want to get user infos of other users, you should use the /api/users/ view instead. /rest-auth/profile/ is
# only meant to get and change infos of your own user.
# ---- Notice 4
# the documentation of profile/ is wrong. there is an open issue for that:
# https://github.com/jazzband/dj-rest-auth/issues/217
urlpatterns = [
    path('', rest_auth_root, name='rest_auth_root'),
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),

    path('me/', UserDetailsView.as_view(), name='rest_user_details'),
    path('password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('registration/', RegisterView.as_view(), name='rest_register'),
    path('registration/verify-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    re_path(r'registration/verify-email/(?P<key>[-:\w]+)/$', VerifyEmailView.as_view(), name='account_confirm_email'),
]
