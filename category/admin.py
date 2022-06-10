from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from category.models import Category, CategoryMPTT, CategoryTreeBeard


class CategoryTreeInline(admin.TabularInline):
    model = CategoryMPTT
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    search_fields = ["name", ]
    ordering = ["name", ]
    inlines = [CategoryTreeInline, ]


class CategoryTreeAdmin(DjangoMpttAdmin):
    list_filter = ["level", ]
    # pass

class MyAdmin(TreeAdmin):
    form = movenodeform_factory(CategoryTreeBeard)

admin.site.register(CategoryTreeBeard, MyAdmin)
admin.site.register(CategoryMPTT, CategoryTreeAdmin)
