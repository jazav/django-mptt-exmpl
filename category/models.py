from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ObjectDoesNotExist
import uuid


# nb = dict(null=True, blank=True)

# def xstr(s):
#     return '' if s is None else str(s)


class CreateTracker(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class CreateUpdateTracker(CreateTracker):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(CreateTracker.Meta):
        abstract = True


class GetOrNoneManager(models.Manager):
    """returns none if object doesn't exist else model instance"""

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None


class Category(CreateTracker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text="Unique ID for Category")
    name = models.CharField(max_length=256, unique=True)
    objects = GetOrNoneManager()

    class Meta:
        db_table = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return f'{self.name}'


class CategoryTree(MPTTModel, CreateUpdateTracker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text="Unique ID for CategoryTree")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        db_table = "category_tree"

    class MPTTMeta:
        order_insertion_by = ['category_id']
        right_attr = 'rgt' # redefine right attribute to be compatible with sqlalchemy-mptt
        left_attr = 'lft'

    def __str__(self):
        return f'{self.category}'
