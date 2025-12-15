from django.contrib.gis.db import models

# Create your models here.
class Admin(models.Model):
    account = models.CharField(unique=True, max_length=64)
    password = models.CharField(max_length=256)
    name = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'admin'
        managed = False


class Building(models.Model):
    name = models.CharField(unique=True, max_length=64)
    address = models.CharField(max_length=256)
    description = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'building'
        managed = False


class Event(models.Model):
    is_active = models.BooleanField(blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    event_name = models.CharField(max_length=64)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image_url = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'event'
        managed = False


class EventEventarea(models.Model):
    pk = models.CompositePrimaryKey('event_id', 'eventarea_id')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    eventarea = models.ForeignKey('Eventarea', on_delete=models.CASCADE)

    class Meta:
        db_table = 'event_eventarea'
        managed = False
        # unique_together = (('event', 'eventarea'),)


class EventStorearea(models.Model):
    pk = models.CompositePrimaryKey('event_id', 'storearea_id')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    storearea = models.ForeignKey('Storearea', on_delete=models.CASCADE)

    class Meta:
        db_table = 'event_storearea'
        # unique_together = (('event', 'storearea'),)
        managed = False


class Eventarea(models.Model):
    is_active = models.BooleanField(blank=True, null=True)
    shape = models.PolygonField(srid=2385)
    description = models.CharField(max_length=256, blank=True, null=True)
    organizer_name = models.CharField(max_length=64)
    organizer_phone = models.CharField(max_length=16)
    type = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'eventarea'
        managed = False


class EventareaMap(models.Model):
    pk = models.CompositePrimaryKey('eventarea_id', 'map_id')
    eventarea = models.ForeignKey(Eventarea, on_delete=models.CASCADE)
    map = models.ForeignKey('Map', on_delete=models.CASCADE)

    class Meta:
        db_table = 'eventarea_map'
        # unique_together = (('eventarea', 'map'),)
        managed = False


class Facility(models.Model):
    is_active = models.BooleanField(blank=True, null=True)
    location = models.PointField(srid=2385)
    description = models.CharField(max_length=256, blank=True, null=True)
    type = models.IntegerField()

    class Meta:
        db_table = 'facility'
        managed = False


class FacilityMap(models.Model):
    pk = models.CompositePrimaryKey('facility_id', 'map_id')
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    map = models.ForeignKey('Map', on_delete=models.CASCADE)

    class Meta:
        db_table = 'facility_map'
        # unique_together = (('facility', 'map'),)
        managed = False


class Map(models.Model):
    building = models.ForeignKey(Building, models.CASCADE)
    floor_number = models.IntegerField()
    detail = models.GeometryCollectionField(srid=2385)

    class Meta:
        db_table = 'map'
        unique_together = (('building', 'floor_number'),)
        managed = False


class Otherarea(models.Model):
    is_active = models.BooleanField(blank=True, null=True)
    shape = models.PolygonField(srid=2385)
    description = models.CharField(max_length=256, blank=True, null=True)
    type = models.IntegerField()
    is_public = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'otherarea'
        managed = False


class OtherareaMap(models.Model):
    pk = models.CompositePrimaryKey('otherarea_id', 'map_id')
    otherarea = models.ForeignKey(Otherarea, on_delete=models.CASCADE)
    map = models.ForeignKey(Map, on_delete=models.CASCADE)

    class Meta:
        db_table = 'otherarea_map'
        managed = False
        # unique_together = (('otherarea', 'map'),)


class Storearea(models.Model):
    is_active = models.BooleanField(blank=True, null=True)
    shape = models.PolygonField(srid=2385)
    description = models.CharField(max_length=256, blank=True, null=True)
    store_name = models.CharField(max_length=64)
    owner_name = models.CharField(max_length=64)
    owner_phone = models.CharField(max_length=16)
    logo_url = models.CharField(max_length=256, blank=True, null=True)
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    api_url = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'storearea'
        managed = False


class StoreareaMap(models.Model):
    pk = models.CompositePrimaryKey('storearea_id', 'map_id')
    storearea = models.ForeignKey(Storearea, on_delete=models.CASCADE)
    map = models.ForeignKey(Map, on_delete=models.CASCADE)

    class Meta:
        db_table = 'storearea_map'
        # unique_together = (('storearea', 'map'),)
        managed = False