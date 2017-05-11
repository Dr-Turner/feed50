import os
from tempfile import mkdtemp

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'app', 'db')
db_file = 'production.db'
db_fullpath = os.path.join(db_path, db_file)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_fullpath
SQLALCHEMY_TRACK_MODIFICATIONS = False    # to disable annoying warnings
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"
