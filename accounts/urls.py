from django.urls import path
from .views import SignUpView, AuthView, SendOtpView

urlpatterns = [
    path('sendotp/', SendOtpView.as_view(), name='sendotp'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('auth/', AuthView.as_view(), name='auth'),
]
