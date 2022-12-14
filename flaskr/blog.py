from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import ipaddress

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created ASC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


def check_duplicate(title, body, id=None):
    if id is None:
        post = get_db().execute(
            'SELECT title, body'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE title = ? AND body = ?',
            (title, body,)
        ).fetchall()
    else:
        post = get_db().execute(
            'SELECT title, body, p.id'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE title = ? AND body = ? AND p.id != ?',
            (title, body, id)
        ).fetchall()

    return post


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        try:
            ipaddress.ip_address(body)
        except ValueError:
            error = 'Not valid ip address.'

        if check_duplicate(title, body):
            error = 'A card with this label and ip address already exists'

        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        try:
            ipaddress.ip_address(body)
        except ValueError:
            error = 'Not valid ip address.'

        # print(check_duplicate(title, body))
        if check_duplicate(title, body, id):
            error = 'A card with this label and ip address already exists'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))



