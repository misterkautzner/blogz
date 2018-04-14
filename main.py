from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(10000), nullable=False)

    def __init__(self, title, body):
        self.title = title
        self.body = body



@app.route('/')
def index():
    return redirect('/blog')


@app.route('/blog') 
def blog():

    blogs = Blog.query.all()

    return render_template('blog.html', title='Build a Blog', blogs=blogs)


@app.route('/add', methods=['GET', 'POST'])
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

        new_blog_post = Blog(title, body)

        db.session.add(new_blog_post)
        db.session.commit()

        return redirect('/blog')

    return render_template('add_form.html', title='Add a Blog Entry')




if __name__ == '__main__':
    app.run()