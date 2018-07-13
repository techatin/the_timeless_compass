from flask import flash, render_template, redirect, session, url_for, request
from flask import g, send_file, make_response, Blueprint
from app import app, db
from app.models import User, Article, Draft, Category
from datetime import datetime
from functools import wraps, update_wrapper
import os

main_blueprint = Blueprint('main', __name__, template_folder='templates')


@main_blueprint.route('/index')
def index():
    return render_template(
        'main/index.html',
        categories=Category.query.all(),
        carousel_articles=Article.query.filter_by(is_carousel=True).all(),
        other_articles=Article.query.filter_by(is_carousel=False, is_index=True).all())


@main_blueprint.route('/article/<int:art_id>')
def article_view(art_id):
    article = Article.query.get(art_id)
    rev_number = article.published_draft

    if not article.is_published:
        return redirect(url_for('main.index'))

    return render_template(
        'main/article.html',
        author=article.author,
        categories=Category.query.all(),
        title=article.title,
        cover_image=article.cover_image,
        fp=''.join(['/admin/documents/', article.folder, '/revision_',
                    str(rev_number), '.md']))


@main_blueprint.route('/category/<int:cat_id>')
def category_view(cat_id):
    category = Category.query.get(cat_id)
    articles = category.articles
    return render_template(
        'main/categories.html',
        categories=Category.query.all(),
        articles=articles,
        name=category.name)


@main_blueprint.route('/')
def home():
    return redirect(url_for('main.index'))
