from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from category.models import Category, CategoryTree


class CategoryTreeInline(admin.TabularInline):
    model = CategoryTree
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


admin.site.register(CategoryTree, CategoryTreeAdmin)
