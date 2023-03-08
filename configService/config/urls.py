from django.db import router
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("country", views.CountryViewSet, basename="country")
router.register("supported-country", views.SupportedCountryViewSet,
                basename="supported-country")
urlpatterns = router.urls
