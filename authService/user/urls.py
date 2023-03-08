from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

from user import views as user_views

router = routers.DefaultRouter()

router.register(r"account", user_views.UserViewSet, basename="account")

urlpatterns = [
    path("get_gender/", user_views.GetEnums.as_view())
]

urlpatterns += router.urls
