from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:BABBAB111999BAB@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def index():

    id = request.args.get("id")
    listings = Blog.query.all()

    if not id:
        return render_template('blog.html', title="Build A Blog",
            listings=listings)
    else:
        name=listings[int(id)-1].title
        body=listings[int(id)-1].body
        return render_template('display_entry.html', 
            name=name, body=body)

@app.route('/newpost', methods=['POST'])
def postform():

    name=request.form['name']
    body=request.form['body']

    title_error=''
    body_error=''

    if name == '':
        title_error='Please fill in the title'
    if body == '':
        body_error="Please fill in the body"

    if not title_error and not body_error:
        new_listing = Blog(name, body)
        db.session.add(new_listing)
        db.session.commit() 
        id=new_listing.id
        return redirect("/blog?id=" + str(id))
    else:
        return render_template('newpost.html',title="Add a Blog",
            title_error=title_error,
            body_error=body_error,
            name=name,
            body=body)


@app.route('/newpost', methods=['GET'])
def getform():

    return render_template('newpost.html',title="Add A Blog")

if __name__ == '__main__':
    app.run()