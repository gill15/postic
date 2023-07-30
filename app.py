from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import render_template, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash


app = Flask(__name__)
app.secret_key = 'your secret key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# This line creates a new Flask web server object
@app.route('/dashboard')
def dashboard():
    return "Welcome to the Dashboard!"


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        # Check if user with the same email already exists
        existing_user = User.query.filter_by(email=email).first()

        # If a user already exists, return an error message
        if existing_user is not None:
            flash('A user with this email already exists. Please use a different email.', 'error')
            return redirect(url_for('signup'))

        # If no user exists with the same email, proceed with creating the new user
        new_user = User(username=username, email=email, password=password_hash)

        db.session.add(new_user)
        db.session.commit()

        # Log in new user and redirect to dashboard
        login_user(new_user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')




@app.route('/test')
def test():
    # Create a new user
    user = User(username='testuser', email='testemail@example.com', password='password123')
    db.session.add(user)
    db.session.commit()
    return 'User added.'

    # Create a new post
    post = Post(title='Test Post', content='This is a test post.', user_id=user.id)
    db.session.add(post)
    db.session.commit()

    # Retrieve all users and posts from the database
    all_users = User.query.all()
    all_posts = Post.query.all()

    return {
        'users': [str(u) for u in all_users],
        'posts': [str(p) for p in all_posts]
    }


# This line configures the database location
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# This line creates a new SQLAlchemy database instance
db = SQLAlchemy(app)

# This is the place where we'll add our routes later on

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return '<User %r>' % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % self.content

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # Verify the password using the built-in Flask check_password_hash method
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        content = request.form.get('content')
        new_post = Post(content=content, user_id=current_user.id)

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('index'))

    posts = Post.query.filter_by(user_id=current_user.id).all()

    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get(post_id)

    if not post:
        return 'Post not found.'

    if request.method == 'POST':
        post.content = request.form.get('content')

        db.session.commit()

        return redirect(url_for('index'))

    return render_template('post.html', post=post)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)

    if not post:
        return 'Post not found.'

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('index'))


# This line runs the Flask web server in a development mode
if __name__ == '__main__':
    app.run(debug=True)
