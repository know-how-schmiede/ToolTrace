from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class ToolForm(FlaskForm):
    name = StringField("Werkzeugname", validators=[Optional(), Length(max=180)])
    category_id = SelectField("Kategorie", coerce=int, validators=[Optional()])
    purpose = StringField("Einsatzzweck", validators=[Optional(), Length(max=255)])
    manufacturer = StringField("Hersteller", validators=[Optional(), Length(max=180)])
    model = StringField("Modell", validators=[Optional(), Length(max=180)])
    inventory_number = StringField("Inventarnummer", validators=[Optional(), Length(max=120)])
    storage_location = StringField("Lagerort", validators=[Optional(), Length(max=255)])
    description = TextAreaField("Beschreibung")
    background_key = SelectField("Hintergrundgroesse", validators=[DataRequired()])
    image = FileField(
        "Werkzeugfoto",
        validators=[
            DataRequired(message="Bitte waehlen Sie ein Werkzeugfoto aus."),
            FileAllowed(["jpg", "jpeg", "png"], "Nur JPEG- und PNG-Dateien sind erlaubt."),
        ],
    )
    submit = SubmitField("Speichern")


class UploadImageForm(FlaskForm):
    background_key = SelectField("Hintergrundgroesse", validators=[DataRequired()])
    image = FileField(
        "Werkzeugfoto",
        validators=[DataRequired(), FileAllowed(["jpg", "jpeg", "png"], "Nur JPEG- und PNG-Dateien sind erlaubt.")],
    )
    submit = SubmitField("Bild hochladen")
