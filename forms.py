from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class SignupForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class TaskForm(FlaskForm):
    title = StringField("Task Title", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Task Description", validators=[DataRequired()])
    status = SelectField(
        "Status",
        choices=[("Pending", "Pending"), ("In Progress", "In Progress"), ("Completed", "Completed")],
        validators=[DataRequired()],
    )
    priority = SelectField(
        "Priority",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")],
        validators=[DataRequired()],
    )
    assignee = SelectField("Assign To", coerce=int, validators=[DataRequired()])
    due_date = DateField("Due Date", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Create Task")


class TaskUpdateForm(FlaskForm):
    title = StringField("Task Title", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Task Description", validators=[DataRequired()])
    status = SelectField(
        "Status",
        choices=[("Pending", "Pending"), ("In Progress", "In Progress"), ("Completed", "Completed")],
        validators=[DataRequired()],
    )
    priority = SelectField(
        "Priority",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")],
        validators=[DataRequired()],
    )
    due_date = DateField("Due Date", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Update Task")


class CommentForm(FlaskForm):
    comment = TextAreaField("Comment", validators=[DataRequired(), Length(max=255)])
    submit = SubmitField("Add Comment")


class TaskStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[("Pending", "Pending"), ("In Progress", "In Progress"), ("Completed", "Completed")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update Status")

