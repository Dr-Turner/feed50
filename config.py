import os
from tempfile import mkdtemp

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app/db/production.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False    # to disable annoying warnings
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"
