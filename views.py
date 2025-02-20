from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask.views import MethodView
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Task, Comment
from forms import SignupForm, LoginForm, TaskForm, CommentForm, TaskUpdateForm, TaskStatusForm
from utils import send_task_email, send_task_update_email, send_task_status_update_email



bcrypt = Bcrypt()


# Home View
class HomeView(MethodView):
    def get(self):
        return render_template('index.html')


# Signup View
class SignupView(MethodView):
    def get(self):
        form = SignupForm()
        return render_template('signup.html', form=form)

    def post(self):
        form = SignupForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for('auth.login'))
        return render_template('signup.html', form=form)


# Login View
class LoginView(MethodView):
    def get(self):
        form = LoginForm()
        return render_template('login.html', form=form)

    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash("Invalid email or password", "danger")
        return render_template('login.html', form=form)


# Logout View
class LogoutView(MethodView):
    def get(self):
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for('home.home'))


# AssignTask view
class AssignTaskView(MethodView):
    @login_required
    def get(self):
        form = TaskForm()
        users = User.query.filter(User.id != current_user.id).all()
        form.assignee.choices = [(user.id, f"{user.first_name} {user.last_name}") for user in users]
        return render_template("assign_task.html", form=form, users=users)

    @login_required
    def post(self):
        form = TaskForm()
        users = User.query.filter(User.id != current_user.id).all()
        form.assignee.choices = [(user.id, f"{user.first_name} {user.last_name}") for user in users]

        if form.validate_on_submit():
            assignee = User.query.get(form.assignee.data)
            if not assignee:
                return redirect(url_for("task.assign_task"))

            new_task = Task(
                title=form.title.data,
                description=form.description.data,
                status=form.status.data,
                priority=form.priority.data,
                assignee_id=form.assignee.data,
                creator_id=current_user.id,
                due_date=form.due_date.data
            )
            db.session.add(new_task)
            db.session.commit()

            send_task_email(new_task)
            
            flash("Task successfully assigned!", "success")
            return redirect(url_for("dashboard.dashboard"))

        return render_template("assign_task.html", form=form, users=users)



# view task -->
class TaskDetailView(MethodView):
    @login_required
    def get(self, task_id):
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return redirect(url_for("dashboard.dashboard"))

        comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.desc()).all()
        form = CommentForm()
        return render_template("taskdetail.html", task=task, comments=comments, form=form)

    @login_required
    def post(self, task_id):
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return redirect(url_for("dashboard.dashboard"))

        form = CommentForm()

        if form.validate_on_submit():
            new_comment = Comment(
                comment=form.comment.data,
                user_id=current_user.id,
                task_id=task.id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("dashboard.task_detail", task_id=task.id))

        comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.desc()).all()
        return render_template("taskdetail.html", task=task, comments=comments, form=form)


# Dashboard View (tasklist related)
class DashboardView(MethodView):
    @login_required
    def get(self):
        users = User.query.all()
        query = Task.query

        assignee = request.args.get('assignee')
        status = request.args.get('status')
        due_date = request.args.get('due_date')

        if assignee:
            query = query.filter(Task.assignee_id == assignee)

        if status:
            query = query.filter(Task.status == status)
        
        if due_date:
            query = query.filter(Task.due_date == due_date)

        tasks = query.all()

        return render_template(
            'tasklist.html',
            name=current_user.first_name,
            users=users,
            tasks=tasks,
            assignee=assignee,
            status=status,
            due_date=due_date
        )

# TaskDelete View 
class TaskDeleteView(MethodView):
    def post(self, task_id):
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
        return redirect(url_for('dashboard.dashboard'))


# UserList View
class UserListView(MethodView):
    def get(self):
        users = User.query.all()
        return render_template("userlist.html", users=users)


# TaskUpdate View
class TaskUpdateView(MethodView):
    @login_required
    def get(self, task_id):
        """Fetch task for update form"""
        task = Task.query.filter_by(id=task_id, creator_id=current_user.id).first()
        if not task:
            return redirect(url_for("dashboard.dashboard"))

        form = TaskUpdateForm(obj=task)
        return render_template("taskupdate.html", form=form, task=task)

    @login_required
    def post(self, task_id):
        """Handle task update submission"""
        task = Task.query.filter_by(id=task_id, creator_id=current_user.id).first()
        if not task:
            return redirect(url_for("dashboard.dashboard"))

        form = TaskUpdateForm(request.form)
        if form.validate_on_submit():
            task.title = form.title.data
            task.description = form.description.data
            task.status = form.status.data
            task.priority = form.priority.data
            task.due_date = form.due_date.data

            db.session.commit()
            send_task_update_email(task)
            return redirect(url_for("dashboard.dashboard"))

        return render_template("taskupdate.html", form=form, task=task)


# TaskStatusUpdate View
class TaskStatusUpdateView(MethodView):
    @login_required
    def get(self, task_id):
        task = Task.query.filter_by(id=task_id).first()

        if not task:
            return redirect(url_for("dashboard.dashboard"))
        
        if task.assignee_id != current_user.id:
            return redirect(url_for("dashboard.dashboard"))
        
        form = TaskStatusForm(obj=task)
        return render_template("task_status_update.html", form=form, task=task)
    
    def post(self, task_id):
        task = Task.query.filter_by(id=task_id).first()

        if not task:
            return redirect(url_for("dashboard.dashboard"))
        
        if task.assignee_id != current_user.id:
            return redirect(url_for("dashboard.dashboard"))
        
        form = TaskStatusForm(request.form)

        if form.validate_on_submit():
            task.status = form.status.data
            db.session.commit()
            send_task_status_update_email(task)
            return redirect(url_for("dashboard.dashboard"))
        return render_template("task_status_update.html", form=form, task=task)


# Blueprint setup for authentication and dashboard
home_bp = Blueprint('home', __name__)
auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
user_bp = Blueprint("user", __name__)
task_bp = Blueprint("task", __name__)


# Add route for Home
home_bp.add_url_rule('/', view_func=HomeView.as_view('home'))

# Add routes for Auth views
auth_bp.add_url_rule('/signup', view_func=SignupView.as_view('signup'))
auth_bp.add_url_rule('/login', view_func=LoginView.as_view('login'))
auth_bp.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))

# Add route for Dashboard view
dashboard_bp.add_url_rule('/list/', view_func=DashboardView.as_view('dashboard'))
dashboard_bp.add_url_rule('/task/<int:task_id>/', view_func=TaskDetailView.as_view('task_detail'))


user_bp.add_url_rule('/users/', view_func=UserListView.as_view('user_list'))

task_bp.add_url_rule('/task/', view_func=AssignTaskView.as_view('assign_task'))
task_bp.add_url_rule('/task/delete/<int:task_id>/', view_func=TaskDeleteView.as_view('task_delete'))
task_bp.add_url_rule('/task/update/<int:task_id>/', view_func=TaskUpdateView.as_view('task_update'))
task_bp.add_url_rule('/task/update_status/<int:task_id>/', view_func=TaskStatusUpdateView.as_view('update_task_status'))

