from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, TextField, SelectField
from wtforms.validators import Length, DataRequired, EqualTo, URL
from wtforms.widgets import TextArea


class PrecisForm(FlaskForm):
    precis_text = StringField('precis', validators=[Length(min=1, max=512)])


class PersonalInfoForm(FlaskForm):
    bios = StringField('bios', validators=[Length(min=1, max=512)], widget=TextArea())
    profile_url = StringField('profile_url', validators=[DataRequired(), URL()])
    name = StringField('name', validators=[Length(min=1, max=64)])


class AddCategory(FlaskForm):
    new_category = SelectField('category', coerce=int)


class CoverForm(FlaskForm):
    image_url = StringField('image_url', validators=[DataRequired(), URL()])


class CategoryForm(FlaskForm):
    name = StringField('name', validators=[Length(min=1, max=32)])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[Length(min=6, max=64)])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class ArticleForm(FlaskForm):
    title = StringField('title', validators=[Length(min=1, max=128)])
    identifier = StringField(
        'identifier',
        validators=[DataRequired(), Length(max=20)])


class ContentForm(FlaskForm):
    file_content = StringField('File content', widget=TextArea(), validators=[DataRequired()])


class UserForm(FlaskForm):
    username = StringField('username', validators=[Length(min=6, max=64)])
    password = PasswordField(
                    'password',
                    validators=[
                        DataRequired(),
                        EqualTo('confirm', 'Password must match')
                    ])
    confirm = PasswordField('confirm password')
    permission = SelectField(
                    'user type',
                    choices=[(0, 'admin'), (1, 'editor'), (2, 'author')],
                    coerce=int)
