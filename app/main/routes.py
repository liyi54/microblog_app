from app import db
from flask import current_app
from app.main import bp
from flask import render_template, flash, redirect, url_for
from .forms import EditProfileForm, FollowForm, PostForm, SearchForm
from flask_login import current_user, login_required
from app.models import User, Post
from flask import request, g
from datetime import datetime
from flask_babel import _, get_locale
from guess_language import guess_language
from app.translate import translate
from flask import jsonify


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is live!'))
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['RESULTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None

    return render_template('main/index.html', title='Home', posts=posts.items, prev_url=prev_url,
                           next_url=next_url, form=form)


@bp.route('/about')
def about():
    return render_template('main/index.html', title='About')


@bp.route('/user/@<username>')
@login_required
def user(username):
    form = FollowForm()
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['RESULTS_PER_PAGE'], False)
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None

    return render_template('main/user.html', prev_url=prev_url, next_url=next_url,
                           user=user, posts=posts.items, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Profile successfully updated"))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', form=form, title='Edit Profile')


@bp.route('/follow/@<username>', methods=['POST'])
@login_required
def follow(username):
    form = FollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are now following %(username)s', username=username)
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/@<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = FollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User %(username)s not found', username=username)
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You have unfollowed %(username)s', username=username)
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['RESULTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('main/index.html', posts=posts.items, next_url=next_url,
                           prev_url=prev_url, title='Explore')


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['from_lang'],
                                      request.form['to_lang'])})

@bp.route('/search', methods=['GET'])
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    # page_u = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page=page, per_page=current_app.config['RESULTS_PER_PAGE'])
    # users, total_u = User.search(g.search_form.q.data, page=page, per_page=current_app.config['RESULTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page+1) if total > page \
                * current_app.config['RESULTS_PER_PAGE'] else None
    # next_url_u = url_for('main.search', q=g.search_form.q.data, page=page_u+1) if total_u > page_u \
                # * current_app.config['RESULTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page-1) if page > 1 else None
    # prev_url_u = url_for('main.search', q=g.search_form.q.data, page=page_u-1) if page_u > 1 else None

    return render_template('main/search.html', title=_('Search'), prev_url=prev_url, next_url=next_url, posts=posts)