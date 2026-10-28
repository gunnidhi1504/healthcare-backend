from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    RegisterView,
    DoctorViewSet,
    PatientViewSet,
    PatientDoctorMappingViewSet,
)

# Router for ModelViewSets
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'mappings', PatientDoctorMappingViewSet, basename='mapping')

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. Authentication APIs
    # -------------------------------------------------------------------------
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token-verify'),

    # -------------------------------------------------------------------------
    # 2. ViewSet Router URLs
    #    - /api/patients/ & /api/patients/<pk>/
    #    - /api/doctors/  & /api/doctors/<pk>/
    #    - /api/mappings/ & /api/mappings/<pk>/ & /api/mappings/<patient_id>/
    # -------------------------------------------------------------------------
    path('', include(router.urls)),
]
