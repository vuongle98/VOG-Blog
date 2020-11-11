import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'keydailam'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CKEDITOR_SERVE_LOCAL=False
    CKEDITOR_FILE_UPLOADER='upload'
    UPLOADED_PATH = os.path.join(basedir, 'uploads') 
    CKEDITOR_ENABLE_CSRF = True
    POSTS_PER_PAGE = 3