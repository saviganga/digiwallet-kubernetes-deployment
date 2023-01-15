from django.urls import path, include
from xauth import views as xauth_views

urlpatterns = [
    path("login/", xauth_views.JWTAuth.as_view()),
    path("logout/", xauth_views.JWTDestroy.as_view()),
]
