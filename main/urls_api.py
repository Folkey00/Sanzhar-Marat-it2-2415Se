# main/urls_api.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_api import ProjectViewSet, TokenLoginView

# Создаем роутер и регистрируем ViewSet
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

# Объединяем маршруты ViewSet и путь к TokenLoginView
urlpatterns = router.urls + [
    path('api/token/', TokenLoginView.as_view(), name='token_login'),
]

