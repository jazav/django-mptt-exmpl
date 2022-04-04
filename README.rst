=======
MPTT in Django: This is an example of usage django, django-mptt and django-mptt-admin projects together
=======
|Django Git| |django-mptt Git| |django-mptt-admin Git| |sqlalchemy-mptt-exmpl Git|

There is a simple database model of two tables: Category (id, name) and CategoryTree (id, category_id, parent_id).
Category is just a plain list of simple items. You can put some stuff in this dictionary to combine them like a tree.
CategoryTree is a hierarchical data structure that using Modified Preorder Tree Traversal (or so called nested set).

Pay your attention that we use UUID data type as PK for all entities (categories and their hierarchies).
You can edit all tables using Django Admin.

*This project is compatible with https://github.com/jazav/sqlalchemy-mptt-exmpl/ project.*

.. |Django Git| image::
   :target: https://github.com/django/django
.. |django-mptt Git|
   :target: https://github.com/django-mptt/django-mptt
.. |django-mptt-admin Git|
   :target: https://github.com/mbraak/django-mptt-admin
.. |sqlalchemy-mptt-exmpl Git|
   :target: https://github.com/jazav/sqlalchemy-mptt-exmpl
.. _sqlalchemy-mptt-exmpl: https://github.com/jazav/sqlalchemy-mptt-exmpl/

