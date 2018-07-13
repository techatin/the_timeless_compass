#!flask/bin/python

from app import db
from app.models import Article

x = Article.query.first()
db.session.delete(x)
db.session.commit()
