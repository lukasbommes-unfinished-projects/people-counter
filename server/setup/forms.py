from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length, Optional


class RoomForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(max=64)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=400)])
    submit = SubmitField("Save changes")


class CameraForm(FlaskForm):
    url = StringField("URL", validators=[InputRequired(), Length(max=256)])
    username = StringField("Username", validators=[Optional(), Length(max=64)])
    password = PasswordField("Password", validators=[Optional(), Length(max=128)])
    rooms = SelectField("Installed in", coerce=int)
    submit = SubmitField("Save changes")
