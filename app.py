from flask import Flask
from flask import redirect, url_for, request

from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask_security import Security
from flask_security import current_user
from flask_security import SQLAlchemyUserDatastore

from config import Configuration


app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)

migrate = Migrate(app=app, db=db)
manager = Manager(app=app)
manager.add_command('db', MigrateCommand)


# Admin

from models import *


class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


class BaseModelView(ModelView):
    def on_model_change(self, form, model, is_created):
        model.generate_slug()
        return super().on_model_change(form, model, is_created)


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


class PostAdminView(AdminMixin, BaseModelView):
    form_columns = ['title', 'body', 'tags']


class TagAdminView(AdminMixin, BaseModelView):
    form_columns = ['name', 'posts']


admin = Admin(app, 'FlaskApp', url='/', index_view=HomeAdminView(name='Home'))
admin.add_view(PostAdminView(Post, db.session))
admin.add_view(TagAdminView(Tag, db.session))


# Flask-security

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)





