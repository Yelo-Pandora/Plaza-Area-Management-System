from core.models import *
from django.db.models import Q

class BaseContext:
    """基础 CRUD Context"""
    def __init__(self, model):
        self.model = model

    def get_by_id(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def list_all(self):
        return self.model.objects.all()

    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)

    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()