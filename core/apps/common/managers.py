from django.db import models
from django.utils import timezone


# class GetOrNoneQuerySet(models.QuerySet):
#     def get_or_none(self, *args, **kwargs):
#         print(self.model)
#         try:
#             return self.get(*args, **kwargs)
#         except self.model.DoesNotExist:
#             return None


class GetOrNoneManager(models.Manager):
    # def get_queryset(self, *args, **kwargs):
    #     return GetOrNoneQuerySet(self.model)
    def get_or_none(self, *args, **kwargs):
        queryset = self.get_queryset()
        try:
            return queryset.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return


class IsDeletedQuerySet(models.QuerySet):
    def delete(self, hard_delete=False):
        if hard_delete:
            return super().delete()
        else:
            return self.update(is_deleted=True, deleted_at=timezone.now())


class IsDeletedManager(GetOrNoneManager):
    def get_queryset(self):
        return IsDeletedQuerySet(self.model).filter(is_deleted=False)

    def unfiltered(self):
        return IsDeletedQuerySet(self.model)

    def hard_delete(self):
        return self.unfiltered().delete(hard_delete=True)


