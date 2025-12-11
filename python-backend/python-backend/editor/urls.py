from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'storearea', views.StoreareaViewSet, basename='storearea')
router.register(r'event', views.EventViewSet, basename='event')

urlpatterns = [
    # 包含路由器生成的所有URL
    path('', include(router.urls)),
]

