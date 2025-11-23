# parcel_data/urls.py
from rest_framework.routers import DefaultRouter
from .views import ParcelViewSet, CriterionViewSet

router = DefaultRouter()
router.register(r'parcels', ParcelViewSet, basename='parcel')
router.register(r'criteria', CriterionViewSet, basename='criterion')

urlpatterns = router.urls
