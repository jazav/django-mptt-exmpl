from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ObjectDoesNotExist
# import uuid


# nb = dict(null=True, blank=True)

# def xstr(s):
#     return '' if s is None else str(s)

APP_LABEL: str = __package__.rsplit('.', 1)[-1]


def get_table_name(model_name: str) -> str:
    return f'{APP_LABEL}_{model_name}'


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
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
    #                       help_text="Unique ID for Category")

    # it is unnecessary to define a primary key, if we use bigint as primary key
    # id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=256, unique=True)
    objects = GetOrNoneManager()

    class Meta:
        db_table = get_table_name("category")
        verbose_name_plural = "categories"

    def __str__(self):
        return f'{self.name}'


class CategoryTree(MPTTModel, CreateUpdateTracker):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
    #                       help_text="Unique ID for CategoryTree")
    # it is unnecessary to define a primary key, if we use bigint as primary key
    # id = models.AutoField(primary_key=True)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = get_table_name("category_tree")

    class MPTTMeta:
        order_insertion_by = ['category_id']
        right_attr = 'rgt' # redefine right attribute to be compatible with sqlalchemy-mptt
        left_attr = 'lft'

    def __str__(self):
        return f'{self.category}'
