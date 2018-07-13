from flask import flash, render_template, redirect, session, url_for, request
from flask import g, send_file, make_response, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from app import app, lm, db
from app.forms import LoginForm, ArticleForm, ContentForm, UserForm, CategoryForm
from app.forms import AddCategory, CoverForm, PrecisForm, PersonalInfoForm
from app.models import User, Article, Draft, Category
from datetime import datetime
from functools import wraps, update_wrapper
import os


admin_blueprint = Blueprint(
    'admin',
    __name__,
    template_folder='templates',
    url_prefix="/admin")


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


@admin_blueprint.route('/documents/<path:path>')
@login_required
@nocache
def send_doc(path):
    # print('VISITED')
    # print(os.stat(os.path.join('app/documents', path)).st_mtime)
    print(os.path.join('admin/documents', path))
    return send_file(os.path.join('admin/documents', path))


@admin_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        # print(username, pwd)

        user = User.query.filter_by(username=username).first()
        if user.check_pwd(pwd):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            print("BOO")
            print(User.query.all())
            flash("Email and password do not match")
            return redirect(url_for('admin.login'))

    return render_template(
        'admin/login.html',
        form=form)
    # if form.validate_on_submit():


@admin_blueprint.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if g.user.permission >= 1:
        return redirect(url_for('admin.index'))

    form = CategoryForm()

    if form.validate_on_submit():
        name = form.name.data
        cat = Category()
        cat.name = name
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('admin.index'))

    return render_template('admin/category.html', form=form)


@admin_blueprint.route('/article/new', methods=['GET', 'POST'])
@login_required
def new_article():
    form = ArticleForm()

    if form.validate_on_submit():
        print("ZZZ")
        title = form.title.data
        time_now = datetime.now()
        folder_name = form.identifier.data

        new_object = Article()
        new_object.title = title
        new_object.created = time_now
        new_object.updated = time_now
        new_object.folder = folder_name
        new_object.author = g.user

        db.session.add(new_object)
        db.session.commit()

        return redirect(url_for('admin.index'))

    return render_template('admin/article.html', form=form)


@admin_blueprint.route('/article/view', methods=['GET', 'POST'])
@login_required
def view_article(art_id):
    article = Article.query.get(art_id)
    form = ArticleForm()

    if form.validate_on_submit():
        title = form.title.data
        time_now = datetime.now()
        folder_name = form.identifier.data

        new_object = Article()
        new_object.title = title
        new_object.updated = time_now

        db.session.add(new_object)
        db.session.commit()

        return redirect(url_for('admin.index'))

    return render_template(
        'admin/article_detail.html',
        article=article,
    )


@admin_blueprint.route('/article/<int:art_id>/draft/new', methods=["POST"])
@login_required
def new_draft(art_id):
    article = Article.query.filter_by(id=art_id).first()

    if article.author != g.user:
        return redirect(url_for('admin.index'))

    time_now = datetime.now()
    draft = Draft()
    draft.revision_number = article.num_draft + 1
    article.num_draft += 1
    draft.article = article
    draft.created = time_now
    draft.updated = time_now

    db.session.add(draft)
    db.session.add(article)
    db.session.commit()

    path = ''.join([
        'app/documents/',
        article.folder])

    file_path = os.path.join(os.getcwd(), path)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    file_path_new = ''.join([str(file_path), '/revision_', str(draft.revision_number), '.md'])

    with open(file_path_new, mode='w') as f:
        f.write("#Start here")

    return redirect(url_for('admin.draft_view', art_id=article.id, draft_id=draft.id))


@admin_blueprint.route('/article/<int:art_id>/delete', methods=["POST"])
@login_required
def delete_article(art_id):
    article = Article.query.get(art_id)

    for draft in article.drafts:
        db.session.delete(draft)

    db.session.delete(article)
    db.session.commit()

    return redirect(url_for('admin.index'))


@admin_blueprint.route('/article/<int:art_id>/draft/<int:draft_id>/send', methods=['POST'])
@login_required
def send_to_editor(art_id, draft_id):
    draft = Draft.query.get(draft_id)
    draft.submit_to_editor = True
    db.session.add(draft)
    db.session.commit()

    return redirect(url_for('admin.index'))


@admin_blueprint.route('/article/<int:art_id>/draft/<int:draft_id>/publish', methods=['POST'])
@login_required
def publish(art_id, draft_id):
    if g.user.permission >= 2:
        return redirect(url_for('admin.index'))
    article = Article.query.get(art_id)
    draft = Draft.query.get(draft_id)
    print(article.title)
    print(draft.revision_number)
    draft.submit_to_editor = False
    article.is_published = True
    article.published_draft = draft.revision_number
    db.session.add(draft)
    db.session.add(article)
    db.session.commit()
    return redirect(url_for('admin.index'))


@admin_blueprint.route('/review')
@login_required
def review_list():
    drafts = Draft.query.filter_by(submit_to_editor=True).all()
    print(drafts)
    return redirect(url_for('admin.index'))


@admin_blueprint.route('/article/<int:art_id>/draft/<int:draft_id>', methods=['GET', 'POST'])
@login_required
def draft_view(art_id, draft_id):
    print(request.method)
    # if request.method == 'POST':
    #     print("POSTED")
    # elif request.method == 'GET':
    #     print('GIT GUD')
    draft = Draft.query.get(draft_id)
    article = Article.query.get(art_id)
    form = ContentForm()

    if article.author != g.user:
        return redirect(url_for('admin.index'))

    path = ''.join([
        'app/admin/documents/',
        article.folder])

    file_path = os.path.join(os.getcwd(), path)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    file_path_new = ''.join([str(file_path), '/revision_', str(draft.revision_number), '.md'])

    if form.validate_on_submit():
        print("Form received")
        content = form.file_content.data
        print(content)
        with open(file_path_new, mode='w') as f:
            f.write(content)

        flash("Draft saved")
        return redirect(url_for('admin.draft_view', art_id=article.id, draft_id=draft.id))

    return render_template(
            'admin/draft_detail.html',
            fp=''.join(['/admin/documents/', article.folder, '/revision_', str(draft.revision_number), '.md']),
            # title=article.title,
            art_id=art_id,
            draft_id=draft_id,
            form=form, read_only=False)


@admin_blueprint.route('/article/<int:art_id>/draft/view/<int:draft_id>', methods=['GET', 'POST'])
@login_required
def draft_view_readonly(art_id, draft_id):

    # print("Request made")
    draft = Draft.query.get(draft_id)
    article = Article.query.get(art_id)
    form = ContentForm()

    if article.author != g.user:
        return redirect(url_for('admin.index'))

    path = ''.join([
        'app/documents/',
        article.folder])

    file_path = os.path.join(os.getcwd(), path)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    file_path_new = ''.join([str(file_path), '/revision_', str(draft.revision_number), '.md'])

    return render_template(
            'admin/draft_detail.html',
            fp=''.join(['/documents/', article.folder, '/revision_', str(draft.revision_number), '.md']),
            # title = article.title,
            form=form, read_only=True)


@admin_blueprint.route('/admin/user', methods=['GET', 'POST'])
@login_required
def new_user():
    if g.user.permission > 0:
        return redirect(url_for('admin.index'))
    form = UserForm()
    if form.validate_on_submit():
        # print("HEY")
        username = form.username.data
        password = form.password.data
        permission = form.permission.data
        new_user = User()
        new_user.username = username
        new_user.set_pwd(password)
        new_user.permission = permission
        db.session.add(new_user)
        db.session.commit()
        print(type(permission))

    return render_template('admin/new_user.html', form=form)


@admin_blueprint.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if g.user.permission > 0 and g.user.id != user_id:
        return redirect(url_for('admin.index'))

    form = PersonalInfoForm()

    if form.validate_on_submit():
        user = User.query.get(user_id)
        user.profile_image = form.profile_url.data
        user.bios = form.bios.data
        user.name = form.name.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.index'))

    return render_template('admin/personal_info.html', form=form)


@admin_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.index'))


@admin_blueprint.route('/index')
@login_required
def index():
    for_review = Draft.query.filter_by(submit_to_editor=True).all()
    categories = Category.query.all()
    category_form = AddCategory()
    category_form.new_category.choices = [(i.id, i.name) for i in categories]
    cover_form = CoverForm()
    precis_form = PrecisForm()
    published_articles = Article.query.filter_by(is_published=True).all()
    return render_template(
        'admin/index.html',
        authenticated=True,
        published_articles=published_articles,
        for_review=for_review,
        categories=categories,
        category_form=category_form,
        cover_form=cover_form,
        precis_form=precis_form)


@admin_blueprint.route('/article/disp', methods=['POST'])
@login_required
def update_article_disp():
    param = request.get_json()
    article = Article.query.get(param['art_id'])
    article.is_index = param['is_index']
    article.is_carousel = param['is_carousel']
    db.session.add(article)
    db.session.commit()

    return redirect(url_for('admin.index'))


@admin_blueprint.route('/article/<int:art_id>/add_cover', methods=['POST'])
@login_required
def add_cover(art_id):
    form = CoverForm()

    if form.validate_on_submit():
        article = Article.query.get(art_id)
        article.cover_image = form.image_url.data
        db.session.add(article)
        db.session.commit()

    return redirect(url_for('admin.index'))


@admin_blueprint.route('/article/<int:art_id>/add_category', methods=['POST'])
@login_required
def add_category_to_article(art_id):
    form = AddCategory()
    categories = Category.query.all()
    form.new_category.choices = [(i.id, i.name) for i in categories]

    if form.validate_on_submit():
        article = Article.query.get(art_id)
        category = Category.query.get(form.new_category.data)
        if category not in article.categories:
            article.categories.append(category)
        db.session.add(article)
        db.session.commit()

    return redirect(url_for('admin.index'))


@admin_blueprint.route('/article/remove_category', methods=['POST'])
@login_required
def remove_category():
    param = request.get_json()
    article = Article.query.get(param['art_id'])
    category = Category.query.get(param['cat_id'])
    if category in article.categories:
        article.categories.remove(category)
        db.session.add(article)
        db.session.commit()
    return redirect(url_for('admin.index'))


@admin_blueprint.route('/article/<int:art_id>/precis', methods=['POST'])
@login_required
def add_precis(art_id):
    form = PrecisForm()

    if form.validate_on_submit:
        article = Article.query.get(art_id)
        article.precis = form.precis_text.data
        db.session.add(article)
        db.session.commit()

    return redirect(url_for('admin.index'))


@admin_blueprint.route('/')
@login_required
def home():
    return redirect(url_for('admin.index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
