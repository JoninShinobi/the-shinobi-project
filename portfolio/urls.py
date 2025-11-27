from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ContactSubmissionViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'contact', ContactSubmissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
