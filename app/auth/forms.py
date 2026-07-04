from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    email = EmailField("E-Mail", validators=[DataRequired(), Email(), Length(max=255)])
    username = StringField("Benutzername", validators=[DataRequired(), Length(min=3, max=80)])
    first_name = StringField("Vorname", validators=[Length(max=120)])
    last_name = StringField("Nachname", validators=[Length(max=120)])
    password = PasswordField("Passwort", validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField(
        "Passwort wiederholen",
        validators=[DataRequired(), EqualTo("password", message="Die Passwoerter stimmen nicht ueberein.")],
    )
    submit = SubmitField("Registrieren")


class LoginForm(FlaskForm):
    email = EmailField("E-Mail", validators=[DataRequired(), Email()])
    password = PasswordField("Passwort", validators=[DataRequired()])
    remember = BooleanField("Angemeldet bleiben")
    submit = SubmitField("Anmelden")
