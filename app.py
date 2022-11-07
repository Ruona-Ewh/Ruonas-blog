from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, SignupForm, PostForm
from werkzeug.security import generate_password_hash, check_password_hash
import os

base_dir = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__)
app.config['SECRET_KEY']= '0a3e3c5c22faae8299f1e60cb63e1247'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'ruona_blog.db')
db = SQLAlchemy(app) 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.Text(60), nullable=False)
    posts = db.relationship('Blogpost', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.firstname}', '{self.lastname}')"


class Blogpost(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    article = db.Column(db.Text , nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
     
    def __repr__(self):
        return f"Blogpost('{self.title}', '{self.date_posted}')"

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()    

@app.route("/")
@app.route("/home")
def index():
    posts = Blogpost.query.all()
    return render_template('index.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful!')
        return redirect(url_for('index'))
    return render_template('signup.html', title='signup', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        old_user = User.query.filter_by(email=form.email.data).first()
        if old_user:
            if check_password_hash(old_user.password, form.password.data):
                flash('Login Successful')
                login_user(old_user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid username or password')
        return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)

@app.route("/post/<int:id>")
def post(id):
    post = Blogpost.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route("/post/<int:id>/delete", methods=['GET'])
@login_required
def delete(id):
    post = Blogpost.query.get_or_404(id)
    if current_user != post.author:
        flash("You are not permitted to delete another user's article")
    db.session.delete(post)
    db.session.commit()
    flash('Article Deleted Successfully')
    return redirect(url_for('index'))


@app.route("/post/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    post = Blogpost.query.get_or_404(id)
    if post.author != current_user:
        flash("You are not permitted to edit another user's article")
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.article = form.article.data
        db.session.commit()
        flash('Article Updated')
        return redirect(url_for('post', id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.article.data = post.article
    return render_template('edit.html', title='Edit', form=form, id=post.id)
    
        
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Blogpost(title=form.title.data, article=form.article.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully')
        return redirect(url_for('index'))
    return render_template('create.html', title='Write', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
