from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired, ValidationError

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()], render_kw={"class": "form-floating"})
    password = PasswordField(label='Password', validators=[DataRequired()], render_kw={"class": "form-floating"})
    submit = SubmitField(label='Login', render_kw={"class": "btn btn-primary btn-block"})

class RegistrationForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()], render_kw={"class": "form-floating"})
    email = StringField(label='Email', validators=[DataRequired()], render_kw={"class": "form-floating"})
    password = PasswordField(label='Password', validators=[DataRequired()], render_kw={"class": "form-floating"})
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired()], render_kw={"class": "form-floating"})
    submit = SubmitField(label='Register', render_kw={"class": "btn btn-primary btn-block"})

class PasswordResetForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()], render_kw={"class": "form-floating"})
    submit = SubmitField(label='Reset Password', render_kw={"class": "btn btn-primary btn-block"})

class LotteryApplicationForm(FlaskForm):
    name = StringField(label="Buyer's Name", validators=[DataRequired()], render_kw={"class": "form-floating"})
    email = StringField(label="Buyer's Email", validators=[DataRequired()], render_kw={"class": "form-floating"})
    number_of_tickets = IntegerField(label="Number of tickets", validators=[DataRequired()], render_kw={"class": "form-floating"})
    lottery_sequence = SelectField(label = "Lottery Sequence", choices=[], validators=[DataRequired()])
    seller = StringField(label="Seller's Name", render_kw={"readonly": True})
    lottery_number_type = SelectField(label = "Lottery Number Type", choices=[("own_number","Buyer wants to choose the lottery number."), ("random_number","Buyer does not want to choose the lottery number")], validators=[DataRequired()])
    submit = SubmitField(label='Next', render_kw={"class": "w-25 btn btn-primary btn-block"})

class OwnTicketNumForm(FlaskForm):
    lottery_number = IntegerField(label="Lottery Number", validators=[DataRequired()], render_kw={"class": "form-floating"})
    submit = SubmitField(label='Submit', render_kw={"class": "w-25 btn btn-primary btn-block"})

    def validate_lottery_number(form, field):
        if len(str(field.data)) != 6:
            raise ValidationError('Lottery Number must be exactly 6 digits.')
                         