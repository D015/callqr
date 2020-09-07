# Профиль с формой создания клиентского места

# User profile view
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    form = ClientPlaceForm()

    if form.validate_on_submit():
        client_place = ClientPlace(name_place=form.name.data)
        db.session.add(client_place)
        db.session.commit()
        flash('Your client_place is now live!')
        return redirect(url_for('user', username=username))

     # page = request.args.get('page', 1, type=int)
    # posts = user.posts.order_by(Post.timestamp.desc()).paginate(
    #     page, app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('user', username=user.username, page=posts.next_num) \
    #     if posts.has_next else None
    # prev_url = url_for('user', username=user.username, page=posts.prev_num) \
    #     if posts.has_prev else None
    return render_template('user.html', user=user, form=form)
    # , posts=posts.items,
    #                        next_url=next_url, prev_url=prev_url)


# для запроса многие ко многим
u17 = db.session.query(user_client_place.c.user_id).filter(user_client_place.c.client_place_id == 20).all()
u21 = ClientPlace.query.filter_by(id=21).first()
u21 = ClientPlace.query.filter(ClientPlace.id == 21).first()

# в email_my.py [0] ???
sender=app.config['ADMINS'][0]



