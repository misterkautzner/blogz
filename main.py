from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


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


@app.route('/')
def index():
    return redirect('/blog')


@app.route('/login')
def login():
    return render_template('login.html', title='Login')
 

@app.route('/blog') 
def blog():

    blog_id = request.args.get('id')

    if blog_id:
        blog = Blog.query.get(blog_id)

        return render_template('blog_post.html', title = blog.title, body=blog.body)
    

    blogs = Blog.query.all()

    return render_template('blog.html', title='Build a Blog', blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def add():
    title_error = ''
    body_error = ''

    if request.method == 'POST':

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

        new_blog_post = Blog(title, body) #, user)

        db.session.add(new_blog_post)
        db.session.commit()
        id = new_blog_post.id

        return redirect('/blog?id={0}'.format(id))

    return render_template('add_form.html', title='Add a Blog Entry')



if __name__ == '__main__':
    app.run()