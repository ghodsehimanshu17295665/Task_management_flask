from flask_mail import Message
from flask import current_app


def send_email(subject, recipient, message_body):
    """Helper function to send an email."""
    mail = current_app.extensions.get("mail")
    if not mail:
        print("Error: Mail instance not found.")
        return
    
    msg = Message(subject, sender=current_app.config["MAIL_USERNAME"], recipients=[recipient], body=message_body)
    mail.send(msg)
    print(f"Email sent to {recipient} successfully!")


def send_task_email(task):
    """Send an email when a new task is assigned."""
    assignee = task.assignee
    if not assignee or not assignee.email:
        print("Error: Assignee email not found.")
        return

    subject = f"New Task Assigned: {task.title}"
    message_body = (
        f"Hello {assignee.first_name},\n\n"
        f"You have been assigned a new task: {task.title}\n"
        f"Description: {task.description}\n"
        f"Priority: {task.priority}\n"
        f"Due Date: {task.due_date}\n\n"
        "Please check your dashboard for more details."
    )
    send_email(subject, assignee.email, message_body)


def send_task_update_email(task):
    """Send an email when a task is updated."""
    if not task.assignee or not task.assignee.email:
        print("Error: Assignee email not found.")
        return

    subject = "Task Updated"
    message_body = (
        f"Dear {task.assignee.first_name},\n\n"
        f"The task '{task.title}' has been updated by {task.creator.first_name}.\n\n"
        "Please check the task details."
    )
    send_email(subject, task.assignee.email, message_body)


def send_task_status_update_email(task):
    """Send an email when the status of a task is updated."""
    if not task.creator or not task.creator.email:
        print("Error: Creator email not found.")
        return

    subject = "Task Status Updated"
    message_body = (
        f"Dear {task.creator.first_name},\n\n"
        f"The status of the task '{task.title}' has been updated by {task.assignee.first_name}.\n\n"
        "Please check the task status for more details."
    )
    send_email(subject, task.creator.email, message_body)
