from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, EventForm
from app.models import User, Event
from app.translate import translate
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = EventForm()
    if form.validate_on_submit():
        language = guess_language(form.event.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        event = Event(body=form.event.data, author=current_user,
                      language=language, date=form.event.date.data)
        db.session.add(event)
        db.session.commit()
        flash(_('Your event is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    events = current_user.followed_events().paginate(
        page, current_app.config['EVENTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=events.next_num) \
        if events.has_next else None
    prev_url = url_for('main.index', page=events.prev_num) \
        if events.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           events=events.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.timestamp.desc()).paginate(
        page, current_app.config['EVENTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=events.next_num) \
        if events.has_next else None
    prev_url = url_for('main.explore', page=events.prev_num) \
        if events.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           events=events.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    events = user.events.order_by(Event.timestamp.desc()).paginate(
        page, current_app.config['EVENTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=events.next_num) if events.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=events.prev_num) if events.has_prev else None
    return render_template('user.html', user=user, events=events.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})
