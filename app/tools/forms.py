from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class ToolForm(FlaskForm):
    name = StringField("Werkzeugname", validators=[DataRequired(), Length(max=180)])
    category_id = SelectField("Kategorie", coerce=int, validators=[Optional()])
    purpose = StringField("Einsatzzweck", validators=[DataRequired(), Length(max=255)])
    manufacturer = StringField("Hersteller", validators=[Length(max=180)])
    model = StringField("Modell", validators=[Length(max=180)])
    inventory_number = StringField("Inventarnummer", validators=[Length(max=120)])
    storage_location = StringField("Lagerort", validators=[Length(max=255)])
    description = TextAreaField("Beschreibung")
    image = FileField(
        "Werkzeugfoto",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Nur JPEG- und PNG-Dateien sind erlaubt.")],
    )
    submit = SubmitField("Speichern")


class UploadImageForm(FlaskForm):
    image = FileField(
        "Werkzeugfoto",
        validators=[DataRequired(), FileAllowed(["jpg", "jpeg", "png"], "Nur JPEG- und PNG-Dateien sind erlaubt.")],
    )
    submit = SubmitField("Bild hochladen")
