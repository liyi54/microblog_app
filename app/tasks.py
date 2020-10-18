import time
import sys
from rq import get_current_job
from app import create_app
from .models import Task, User, Post
from app import db
from app.email import send_email
from flask import render_template
import json

app = create_app()
app.app_context().push()

def set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(), 'progress': progress})

        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_posts(user_id):
    try:
        user = User.query.get(user_id)
        set_task_progress(0)
        data = []
        i = 0
        total_posts = user.posts.count()
        for post in user.posts.order_by(Post.timestamp.asc()):
            data.append({'body': post.body,
                         'timestamp': post.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            set_task_progress(100 * i // total_posts)

        send_email('[Microblog] Your posts', app.config['ADMINS'][0],
                   text_body=render_template('email/export_posts.txt'), html_body=render_template(
                'email/export_posts.html'), recipients=[user.email], attachments=[('posts.json', 'application/json',
                                                                                   json.dumps({'posts': data},
                                                                                  indent=4))], sync=True)
    except:
        app.logger.error('Unhandled exception', exec_info=sys.exc_info())
    finally:
        set_task_progress(100)

# def task(seconds):
#     job = get_current_job()
#     print("Starting task")
#     for i in range(seconds):
#         job.meta['progress'] = 100.0*i/seconds
#         job.save_meta()
#         print(i)
#         time.sleep(1)
#     job.meta['progress'] = 100.0
#     job.save_meta()
#     print("Task Ended")