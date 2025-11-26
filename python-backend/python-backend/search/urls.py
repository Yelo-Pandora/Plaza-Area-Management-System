from django.urls import path
from . import views

urlpatterns = [
    # Search店铺功能
    path('storearea/<int:storearea_id>/', views.storearea_by_id, name='storearea-by-id'),
    path('storearea/search/', views.storearea_search, name='storearea-search'),
    path('storearea/list/', views.storearea_list_by_type, name='storearea-list-by-type'),
    path('storearea/<int:storearea_id>/events/', views.storearea_events, name='storearea-events'),

    # Search活动功能
    path('event/<int:event_id>/', views.event_by_id, name='event-by-id'),
    path('event/search/', views.event_search, name='event-search'),
    path('event/list/', views.event_list_by_type, name='event-list-by-type'),
    path('event/<int:event_id>/areas/', views.event_areas, name='event-areas'),
]