from app import db
from hashlib import md5
from datetime import datetime


categories = db.Table('categories',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
)


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)


class Media(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))


class Draft(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    revision_number = db.Column(db.Integer)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    submit_to_editor = db.Column(db.Boolean, default=False)
    has_response = db.Column(db.Boolean, default=False)


class Article(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, unique=True)
    folder = db.Column(db.String(128), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    drafts = db.relationship('Draft', backref='article', lazy=True)
    num_draft = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    is_carousel = db.Column(db.Boolean, default=False)
    is_index = db.Column(db.Boolean, default=False)
    cover_image = db.Column(db.String(512))
    precis = db.Column(db.String(512))
    published_draft = db.Column(db.Integer, default=0)
    categories = db.relationship(
                'Category',
                secondary=categories,
                lazy='subquery',
                backref=db.backref('articles', lazy=True))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64))
    profile_image = db.Column(db.String(512))
    bios = db.Column(db.String(512))
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(32))
    articles = db.relationship('Article', backref='author', lazy=True)
    permission = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % (self.username)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def get_permission(self):
        return ['admin', 'editor', 'author'][self.permission]

    def set_pwd(self, new_pwd):
        self.password = md5((new_pwd+"hsterisluv").encode()).hexdigest()

    def check_pwd(self, new_pwd):
        return md5(
                (new_pwd+"hsterisluv").encode()
            ).hexdigest() == self.password
