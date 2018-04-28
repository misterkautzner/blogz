from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abcde'  


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(10000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():

    print()
    print('Before Request')
    print()

    allowed_routes = ['login', 'blog', 'index', 'signup']

    if request.endpoint not in allowed_routes and 'user' not in session:

        print()
        print('Not logged in')
        print()

        return redirect('/login')

@app.route('/')
def index():
    
    users = User.query.all()
    return render_template('index.html', title='Home', users=users)

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if not (username and password and verify):
            flash('One or more of the fields are invalid.')
            return redirect('/signup')

        if password != verify:
            flash('The passwords you entered don\'t match.')
            return redirect('/signup')

        existing_user = User.query.filter_by(username = username).first()

        if existing_user:
            flash('That username already exists')
            return redirect('/signup')

        if len(username) < 3:
             flash('Username must be at least 3 characters long.')
             return redirect('/signup')
             
        if len(password) < 3:
            flash('Password must be at least 3 characters long.')
            return redirect('/signup')

        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created!', 'success') 
        session['user'] = username
        return redirect('/newpost')

    return render_template('/signup.html', title='Signup')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            if password == existing_user.password:
                session['user'] = username
                return redirect('/newpost')
            else:
                flash('The password you entered is incorrect.', 'error')
                return redirect('/login')

        else:
            flash('The username you entered is not valid.', 'error')
            return redirect('/login')

    return render_template('login.html', title='Login')
  
@app.route('/logout')
def logout():
    del session['user']
    return redirect('/blog')

    
@app.route('/blog') 
def blog():  

    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)

        return render_template('blog_post.html', title = blog.title, blog=blog)

    user_id = request.args.get('user')
    if user_id:
        user = User.query.get(user_id)

        if not user:   
            flash('User does not exist')
            return redirect('/blog')

        blogs = Blog.query.filter_by(user=user).all()
        return render_template('user_posts.html', title=user.username, blogs=blogs)
    

    blogs = Blog.query.all()

    return render_template('blog.html', title='Blogz', blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def add():
    title_error = ''
    body_error = ''

    if request.method == 'POST':

        print()
        print('New Post')
        print()

        title = request.form['title']
        body = request.form['body']

        existing_title = Blog.query.filter_by(title=title).first()

        if existing_title:
            title_error = 'There is already a blog post with the title you entered.'

        if not title:
            title_error = 'You must enter a title.'

        if not body:
            body_error = 'You must enter a body for your blog post.' 

        if title_error or body_error:
            return render_template('add_form.html', title='Add a Blog Entry', title_error = title_error, body_error = body_error, blog_title=title, body=body)

        username = session['user']
        user = User.query.filter_by(username = username).first()

        new_blog_post = Blog(title, body, user)

        db.session.add(new_blog_post)
        db.session.commit()
        id = new_blog_post.id

        return redirect('/blog?id={0}'.format(id))

    print()
    print('New Post Page')
    print()

    return render_template('add_form.html', title='Add a Blog Entry')



if __name__ == '__main__':
    app.run()