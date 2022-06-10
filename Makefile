# Cosmetics
BOLD_BLACK := "\e[1;30m"
BOLD_RED := "\e[1;31m"
BOLD_GREEN := "\e[1;32m"
BOLD_YELLOW := "\e[1;33m"
BOLD_BLUE := "\e[1;34m"
BOLD_PURPLE := "\e[1;35m"
BOLD_CYAN := "\e[1;36m"
BOLD_WHITE := "\e[1;37m"

NC := "\e[0m"

# Shell Functions
INFO := @bash -c '\
  printf $(BOLD_GREEN); \
  echo "=> $$1"; \
  printf $(NC)' SOME_VALUE

.PHONY: rm_migrations make_migrations migrate create_superuser

rm_migrations:
	@ find . -type f -path '*migrations*/*' -name '*.py' ! -name '__init__.py' -delete
	${INFO} "All migrations removed"
make_migrations:
	@ python manage.py makemigrations
	${INFO} "All migrations created"
update_migrations:
	$(MAKE) rm_migrations make_migrations
migrate:
	@ python manage.py migrate
	${INFO} "All migrations migrated"
create_superuser:
#	@ echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
#	User.objects.create_superuser('admin', 'admin@myproject.com', 'admin')" \
#	| python manage.py shell
	@ python manage.py create_project_users
	${INFO} "User admin created"
load:
	@ python manage.py load_initial_data
	${INFO} "Initial data loaded"
delete_renditions:
	@ python manage.py delete_renditions
	${INFO} "Renditions deleted"
total_reset:
	@ python manage.py total_reset
	${INFO} "Total reset completed"

# VENV management
pip_upgrade_pip:
	@ python -m pip install --upgrade pip
	${INFO} "Pip upgraded"
pip_upgrade_setup:
	@ python -m pip install --upgrade setuptools
	${INFO} "Setup upgraded"
pip_install:
	$(MAKE) pip_upgrade_pip pip_upgrade_setup
# Use this command if pip has circular dependencies
	@ pip install --use-deprecated=legacy-resolver -r requirements.txt
	@# pip install -r requirements.txt
	${INFO} "Requirements installed"
pip_uninstall:
	@ pip freeze | xargs pip uninstall -y
	${INFO} "All packages uninstalled"
pip_update:
	$(MAKE) pip_upgrade_pip pip_upgrade_setup
	@ pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
	${INFO} "All packages updated"