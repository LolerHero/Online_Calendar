from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Event
from app.translate import translate
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(body=form.event.data,
                      date=form.date.data, author=current_user)
        db.session.add(event)
        db.session.commit()
        flash('Your event is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    events = current_user.followed_events().paginate(
        page, app.config['EVENTS_PER_PAGE'], False)
    next_url = url_for('index', page=events.next_num) \
        if events.has_next else None
    prev_url = url_for('index', page=events.prev_num) \
        if events.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           events=events.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.timestamp.desc()).paginate(
        page, app.config['EVENTS_PER_PAGE'], False)
    next_url = url_for('explore', page=events.next_num) \
        if events.has_next else None
    prev_url = url_for('explore', page=events.prev_num) \
        if events.has_prev else None
    return render_template("index.html", title='Explore', events=events.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    events = user.events.order_by(Event.timestamp.desc()).paginate(
        page, app.config['EVENTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=events.next_num) \
        if events.has_next else None
    prev_url = url_for('user', username=user.username, page=events.prev_num) \
        if events.has_prev else None
    return render_template('user.html', user=user, events=events.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})
