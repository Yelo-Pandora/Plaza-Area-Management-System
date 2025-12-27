from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'storearea', views.StoreareaViewSet, basename='editor_storearea')
router.register(r'event', views.EventViewSet, basename='editor_event')
router.register(r'eventarea', views.EventareaViewSet, basename='editor_eventarea')
router.register(r'otherarea', views.OtherareaViewSet, basename='editor_otherarea')
router.register(r'facility', views.FacilityViewSet, basename='editor_facility')
router.register(r'map', views.MapEditorViewSet, basename='editor_map')

urlpatterns = [
    # 包含路由器生成的所有URL
    path('', include(router.urls)),
]

