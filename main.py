from flask import Flask, request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ThisisBlogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'cookie'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))



    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','signup_complete','list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form ['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        elif not user:
            username_error = "User does not exist, please create an account below"
            return render_template('login.html',username_error=username_error)
        elif user and user.password != password:
            password_error = "Username and Password do not match, please try again"
            return render_template('login.html',password_error=password_error)

    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

def is_blank(input):
    if input:
        return False
    else:
        return True

def length(input):
    if len(input) > 2 and len(input) < 21:
        return True
    else:
        return False

@app.route('/signup', methods=['POST', 'GET'])
def signup_complete():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form ['password']
        verify = request.form ['verify']

        username_error = ""
        password_error = ""
        verify_password_error = ""

        count_error = "must be 3-20 characters"
        spaces_error = "cannot contain spaces"
        #TODO - validate users data

        existing_user = User.query.filter_by(username=username).first()
        if is_blank(password):
            password_error = "Please provide a password"
            password = ''
            verify = ''
        elif not length(password):
            password_error = "Password " + count_error
            password = ''
            verify_password = ''
            verify_password_error = ''
        else:
            if " " in password:
                password_error = "Password " + spaces_error
                password = ''
                verify_password = ''
                verify_password_error = ''

        if password != verify:
            verify_password_error = "Passwords do not match"
            password = ''
            verify_password = ''
            password_error = 'Passwords do not match'

        if is_blank(username):
            username_error = "Please provide a username"
            password = ''
            verify_password = ''
        elif not length(username):
            username_error = "Username " + count_error
            password = ''
            verify_password = ''
        else:
            if " " in username:
                username_error = "Username " + spaces_error
                password = ''
                verify_password = ''

    if not username_error and not password_error and not verify_password_error and not existing_user:
        new_user = (User(username, password))
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/newpost')
    else:
        return render_template('signup.html', username_error=username_error, username=username,
        password_error=password_error, password=password, verify_password_error=verify_password_error,
        verify_password=verify_password)



@app.route('/', methods = ['GET','POST'])
def list_blogs():
    all_users = User.query.filter_by(username="username").all()
    return render_template("index.html",users=all_users)




@app.route('/blog', methods = ["GET","POST"])
def ind_blog():
    post_id = request.args.get('id')
    owner = User.query.filter_by(username= session['username']).first()
    if (post_id):
        view_post = Blog.query.get(post_id)
        return render_template('view-post.html', view_post=view_post)
    else:
        all_blog_posts = Blog.query.all()
        return render_template('blog.html', blogs=all_blog_posts)



@app.route('/newpost', methods = ['POST','GET'])
def new_post():
    owner = User.query.filter_by(username = session['username']).first()
    if request.method == 'POST':
        title = request.form['blog-title']
        body = request.form['blog']
        if len(title) == 0:
            flash("Please provide a title for your post")
        elif len(body) == 0:
            flash("Please provide an entry for your post")
        else:
            new_post = Blog(title,body,owner)
            db.session.add(new_post)
            db.session.commit()
            post_link = "/blog?id=" + str(new_post.id)
            return redirect(post_link)


    return render_template('newpost.html')


@app.route("/logout", methods=['POST'])
def logout():
    del session['username']
    return redirect("/login")




#owner = User.query.filter_by(email = session['email']).first()

#if request.method == 'POST':
#    task_name = request.form['task']
#    new_task = Blog(task_name, owner)
#    db.session.add(new_task)
#    db.session.commit()

#tasks = Task.query.filter_by(completed=False, owner=owner).all()
#completed_tasks = Task.query.filter_by(completed=True, owner=owner).all()
#return render_template('todos.html',title="Get It Done!", tasks=tasks,
#completed_tasks=completed_tasks)



if __name__ == '__main__':
    app.run()
