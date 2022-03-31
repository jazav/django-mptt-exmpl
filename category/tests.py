from django.test import TestCase
from category.models import Category, CategoryTree


class CategoryTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name="category_1")

    def test_category_get(self):
        """Just get appropriate category"""
        try:
            cat1 = Category.objects.get(name="category_1")
        except Category.DoesNotExist:
            self.fail("cat1 doesn't exist")

        self.assertEqual('category_1', cat1.name)

    def test_category_unique(self):
        from django.db import IntegrityError
        try:
            Category.objects.create(name="category_1")
        except IntegrityError as e:
            self.assertEqual('UNIQUE constraint failed: category.name', e.args[0])

    def test_category_doesntexist(self):
        cat_count = Category.objects.filter(name="category_3").count()
        self.assertEqual(0, cat_count)


class CategoryTreeTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name="category_1")
        Category.objects.create(name="category_2")

    def test_create_root(self):
        cat1: Category = Category.objects.get(name="category_1")
        tree_root: CategoryTree = CategoryTree.objects.create(category=cat1)
        self.assertIsNone(tree_root.parent)
        tree_root.delete()

    def test_create_child(self):
        cat1: Category = Category.objects.get(name="category_1")
        cat2: Category = Category.objects.get(name="category_2")
        tree_root: CategoryTree = CategoryTree.objects.create(category=cat1)
        tree_node: CategoryTree = CategoryTree.objects.create(category=cat2, parent=tree_root)

        self.assertEqual('category_2', tree_node.category.name)
        tree_node.delete()
        tree_root.delete()
