from django.urls import path
from . import views

urlpatterns = [
    # Search店铺功能
    path('storearea/<int:storearea_id>/', views.storearea_by_id, name='storearea-by-id'),
    path('storearea/search/', views.storearea_search, name='storearea-search'),
    path('storearea/list/', views.storearea_list_by_type, name='storearea-list-by-type'),
    path('storearea/<int:storearea_id>/events/', views.storearea_events, name='storearea-events'),

    # 新增的店铺区域功能
    path('storearea/<int:storearea_id>/map/', views.storearea_map_ids, name='storearea-map-ids'),
    path('storearea/list/map/', views.storearea_ids_by_map_and_type, name='storearea-ids-by-map-type'),
    path('storearea/list/all_by_map/', views.all_storearea_ids_by_map, name='all-storearea-ids-by-map'),

    # Search活动功能
    path('event/<int:event_id>/', views.event_by_id, name='event-by-id'),
    path('event/search/', views.event_search, name='event-search'),
    path('event/list/', views.event_list_by_type, name='event-list-by-type'),
    path('event/<int:event_id>/areas/', views.event_areas, name='event-areas'),

    # 新增的活动区域功能
    path('eventarea/<int:eventarea_id>/', views.eventarea_by_id, name='eventarea-by-id'),
    path('eventarea/list/ids_by_map_type/', views.eventarea_ids_by_map_and_type, name='eventarea-ids-by-map-type'),
    path('eventarea/<int:eventarea_id>/map/', views.eventarea_map_ids, name='eventarea-map-ids'),
    path('eventarea/list/all_by_map/', views.all_eventarea_ids_by_map, name='all-eventarea-ids-by-map'),

    # 新增的设施功能
    path('facility/<int:facility_id>/', views.facility_by_id, name='facility-by-id'),
    path('facility/list/ids_by_map_type/', views.facility_ids_by_map_and_type, name='facility-ids-by-map-type'),
    path('facility/<int:facility_id>/map/', views.facility_map_ids, name='facility-map-ids'),
    path('facility/list/all_by_map/', views.all_facility_ids_by_map, name='all-facility-ids-by-map'),

    # 新增的其他区域功能
    path('otherarea/<int:otherarea_id>/', views.otherarea_by_id, name='otherarea-by-id'),
    path('otherarea/list/ids_by_map_type/', views.otherarea_ids_by_map_and_type, name='otherarea-ids-by-map-type'),
    path('otherarea/<int:otherarea_id>/map/', views.otherarea_map_ids, name='otherarea-map-ids'),
    path('otherarea/list/all_by_map/', views.all_otherarea_ids_by_map, name='all-otherarea-ids-by-map'),
]