from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventareaViewSet, OtherareaViewSet, EventViewSet, StoreareaViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'eventarea', EventareaViewSet, basename='management_eventarea')
router.register(r'otherarea', OtherareaViewSet, basename='management_otherarea')
router.register(r'event', EventViewSet, basename='management_event')
router.register(r'storearea', StoreareaViewSet, basename='management_storearea')

urlpatterns = [
    # 包含路由器生成的所有URL
    path('', include(router.urls)),
]
