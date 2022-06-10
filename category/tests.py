# tests.py
import logging

from django.test import TestCase

from category.models import Category, CategoryMPTT, CategoryTreeBeard

logger = logging.getLogger(__name__)


class Category_TestCase(TestCase):
    def setUp(self):
        """Step Arrange: Create test category"""
        Category.objects.create(name="category_1")
        logger.debug("category has been created successfully")

    def test_category_get(self):
        """Step Act: Just get appropriate category"""
        try:
            cat1 = Category.objects.get(name="category_1")
        except Category.DoesNotExist:
            self.fail("cat1 doesn't exist")
        # Step Assert:
        self.assertEqual('category_1', cat1.name)

    def test_category_not_exist(self):
        cat_count = Category.objects.filter(name="category_3").count()
        self.assertEqual(0, cat_count)


class CategoryMPTT_TestCase(TestCase):
    def setUp(self):
        categories = [Category(name=f"category_{i}") for i in range(1, 10)]
        Category.objects.bulk_create(categories)
        logger.debug("categories have been created successfully")

    def test_create_root(self):
        cat1: Category = Category.objects.get(name="category_1")
        tree_root: CategoryMPTT = CategoryMPTT.objects.create(category=cat1)
        logger.debug("root has been created successfully")
        self.assertIsNone(tree_root.parent)
        tree_root.delete()

    def test_create_child(self):
        cat1: Category = Category.objects.get(name="category_1")
        cat2: Category = Category.objects.get(name="category_2")

        tree_root: CategoryMPTT = CategoryMPTT.objects.create(category=cat1)
        tree_node: CategoryMPTT = CategoryMPTT.objects.create(category=cat2, parent=tree_root)

        logger.debug("root and child node have been created successfully")

        self.assertEqual('category_2', tree_node.category.name)
        tree_node.delete()
        tree_root.delete()

    def test_update_node(self):
        cat1: Category = Category.objects.get(name="category_1")
        cat2: Category = Category.objects.get(name="category_2")

        tree_root: CategoryMPTT = CategoryMPTT.objects.create(category=cat1)
        tree_node: CategoryMPTT = CategoryMPTT.objects.create(category=cat2, parent=tree_root)

        logger.debug("root and child node have been created successfully")

        self.assertEqual('category_2', tree_node.category.name)
        tree_node.delete()
        tree_root.delete()


class CategoryTreebeard_TestCase(TestCase):

    def test_create_root(self):
        tree_root: CategoryTreeBeard = CategoryTreeBeard.add_root(name="category_1")
        logger.debug("root has been created successfully")
        self.assertEqual(True, tree_root.is_root(), "Node isn't a root")
        tree_root.delete()

    def test_create_child(self):
        tree_root: CategoryTreeBeard = CategoryTreeBeard.add_root(name="category_1")
        tree_node: CategoryTreeBeard = CategoryTreeBeard.add_child(tree_root, name="category_2")

        logger.debug("root and child node have been created successfully")

        self.assertEqual('category_2', tree_node.name)
        tree_node.delete()
        tree_root.delete()