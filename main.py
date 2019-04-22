from flask import Flask, request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:K@tie007@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'cookie'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))



    def __init__(self,title,body):
        self.title = title
        self.body = body

@app.route('/blog', methods = ["GET","POST"])
def blog():
    post_id = request.args.get('id')
    if (post_id):
        view_post = Blog.query.get(post_id)
        return render_template('view-post.html', view_post=view_post)
    else:
        all_blog_posts = Blog.query.all()
        return render_template('blog.html', blogs=all_blog_posts)



@app.route('/newpost', methods = ['POST','GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['blog-title']
        body = request.form['blog']
        if len(title) == 0:
            flash("Please provide a title for your post")
        elif len(body) == 0:
            flash("Please provide an entry for your post")
        else:
            new_post = Blog(title,body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog')



    return render_template('newpost.html')

















if __name__ == '__main__':
    app.run()
