import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'testing.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


CSRF_ENABLED = True


SECRET_KEY = 'wn6s0ge31x'

ADMIN_PASSWORD = 'root'

ROLE_USER = 0
ROLE_ADMIN = 1
