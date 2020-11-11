from app import app, db
from flask import Flask, render_template, url_for, redirect, flash, request, send_from_directory, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, PostForm
from app.models import User, Post
from werkzeug.urls import url_parse
import os
from flask_ckeditor import upload_fail, upload_success
from multiprocessing import Value

counter = Value('i', 0)

@app.route('/')
@app.route('/index')
def index():
    with counter.get_lock():
        counter.value += 1
        out = counter.value
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    print(out)
    return render_template('index.html', title='Trang chủ', posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/admin')
@login_required
def admin_page():
    role = current_user.role
    if role != 1:
        flash('Bạn không thể vào đây.')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    page2 = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_post_url = url_for('admin_page', page=posts.next_num) \
        if posts.has_next else None
    prev_post_url = url_for('admin_page', page=posts.prev_num) \
        if posts.has_prev else None


    users = User.query.order_by(User.id.asc()).paginate(
        page2, app.config['POSTS_PER_PAGE'], False)
    next_user_url = url_for('admin_page', page=users.next_num) \
        if users.has_next else None
    prev_user_url = url_for('admin_page', page=users.prev_num) \
        if users.has_prev else None

    return render_template('admin.html', title='Admin page', posts=posts.items, users=users.items, \
        next_post_url=next_post_url, prev_post_url=prev_post_url, \
        next_user_url=next_user_url, prev_user_url=prev_user_url)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Sai tài khoản hoặc mật khẩu")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page= url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Đăng nhập', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Đã đăng ký thành công.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Đăng ký', form=form)

@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        matches = Post.query.filter(Post.title == form.title.data).count()
        if matches:
            flash('Bài này đã tồn tại.')
            return redirect(url_for('post'))
        post = Post(title=form.title.data, description=form.description.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Đã lưu')
        return redirect(url_for('post'))
    return render_template('post.html', title='Create post', form=form)


@app.route('/view/<slug>')
def view_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if post is None:
        flash('Post not found.')
        return redirect(url_for('index'))

    return render_template('view.html', title=post.title, post=post)

@app.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    form = PostForm()
    if post is None:
        flash('Bài này có đâu mà sửa.')
        return redirect(url_for('index'))
    if post.author == current_user:
        if form.validate_on_submit():
            post.title = form.title.data
            post.description = form.description.data
            post.content = form.content.data
            db.session.commit()
            flash('Đã lưu')
            return redirect(url_for('edit_post', slug=post.slug))
        
        elif request.method == 'GET':
            form.title.data = post.title
            form.description.data = post.description
            form.content.data = post.content
    else:
        flash('Không thể sửa bài của người khác')
        return redirect(url_for('index'))
    return render_template('post.html', post=post, title=post.title, form=form)


@app.route('/post/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if post.author == current_user or current_user.role == 1:
        db.session.delete(post)
        db.session.commit()
        flash('Đã xóa')
        return redirect(url_for('index'))
    else:
        flash('Không xóa bài của người khác')
        return redirect(url_for('index'))

### User ###
@app.route('/user/delete-user/<id>')
@login_required
def delete_user(id):
    role = current_user.role
    if role != 1:
        flash('Không có quyền xóa.')
        return redirect(url_for('admin_page'))
    user = User.query.filter_by(id=id).first()
    if current_user == user:
        flash('Đừng xóa chính bạn chứ.')
        return redirect(url_for('admin_page'))
    user.deleted = True
    db.session.commit()
    flash('Đã xóa')
    return redirect(url_for('admin_page'))

@app.route('/user/active/<id>')
@login_required
def active_user(id):
    role = current_user.role
    if role != 1:
        flash('Không có quyền.')
    user = User.query.filter_by(id=id).first()
    if current_user == user:
        flash('Bạn có bị đâu.')
        return redirect(url_for('admin_page'))
    user.deleted = False
    db.session.commit()
    flash('Xong')
    return redirect(url_for('admin_page'))

@app.route('/user/edit-profile/<id>')
def edit_profile(id):
    flash('not working :)')
    return redirect(url_for('index'))

@app.route('/user/<username>')
def view_user(username):
    flash('not working :)')
    return redirect(url_for('index'))



##### CKEditor #####
@app.route('/files/<filename>')
@login_required
def uploaded_files(filename):
    path = app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)

import uuid

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    unique_filename = str(uuid.uuid4())
    f.filename = unique_filename + '.' + extension
    f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url=url)

