import datetime
import pytz
from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lfZZv7WvYYIp9H4A@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "b'\xf7\x96\xd6\xc1\x98\xa2OU\x85{\xeb\xc4\xd4\r\xa7\xe3%]\x08\xfa\xc9U`\x9a'"
central = pytz.timezone('America/Chicago')

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
      
@app.before_request
def require_login():
    allowed_routes=['login','signup','blog','index','static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():
    login_error=''
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username']=username
            return redirect('/blog/newpost')
        if not user:
            login_error = "Invalid username"
        else:
            login_error = "Invalid password"

    return render_template('login.html', title='Login',login_error=login_error)

@app.route('/signup', methods=['POST','GET'])
def signup():

    user_error = ''
    pass_error = ''
    verify_error = ''
    username = ''

    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        verify=request.form['verify']

        #TODO- validate users data
    
        if len(username) < 3 or ' ' in username:
            user_error = "That's not a valid username"
            username=''
        else:
            existing_user=User.query.filter_by(username=username).first()
            if existing_user:
                user_error = "That username is already taken"
                username=''
    
        if len(password) < 3 or ' ' in password:
            pass_error = "That's not a valid password"
    
        if verify != password:
            verify_error = "Passwords don't match."

        if not user_error and not pass_error and not verify_error:
            new_user=User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=username
            return redirect('/blog/newpost')

    return render_template('signup.html', title='Signup',user_error=user_error,
        pass_error=pass_error,
        verify_error=verify_error,
        username=username,
        password='',
        verify='')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog():

    id = request.args.get("id")
    userId = request.args.get("user")

    if not id and not userId:
        # Query the blog table to create a list of all existing blog entries
        # in descending order by publication date, so that the most
        # recent blog entries appear first. This list will be rendered
        # on the main blog page. Note: The publication date is stored
        # in the database as UTC, but will be displayed in local time.

        listings = Blog.query.order_by(Blog.pub_date.desc()).all()
        for listing in listings:
            listing.pub_date=pytz.utc.localize(listing.pub_date).astimezone(central)
        return render_template('blog.html', title="Blog Posts!",
            listings=listings)
    elif not userId:
        # From the blog main page, when a user clicks on a blog entry's title,
        # the entry will be displayed by itself, on its own individual entry page.

        listing = Blog.query.filter_by(id=id).first()
        owner_id=listing.owner_id
        name=listing.title
        body=listing.body
        username=listing.owner.username
        pubdate=pytz.utc.localize(listing.pub_date).astimezone(central)
        return render_template('display_entry.html', 
            name=name, body=body, pubdate=pubdate, username=username, owner_id=owner_id)
    else:
        # From the home page, when a user clicks on a blog user's name,
        # query the blog table to get a list of all existing blog entries
        # owned by that user.

        owner = User.query.filter_by(id=userId).first()
        listings = Blog.query.filter_by(owner=owner).order_by(Blog.pub_date.desc()).all()
        for listing in listings:
            listing.pub_date=pytz.utc.localize(listing.pub_date).astimezone(central)
        return render_template('blog.html', title="Blog Posts!",
            listings=listings)

@app.route('/blog/newpost', methods=['POST'])
def postform():

    owner = User.query.filter_by(username=session['username']).first()

    name=request.form['name']
    body=request.form['body']

    title_error=''
    body_error=''

    if name == '':
        title_error='Please fill in the title'
    if body == '':
        body_error="Please fill in the body"

    if not title_error and not body_error:
        new_listing = Blog(name, body, owner)
        db.session.add(new_listing)
        db.session.commit() 
        id=new_listing.id
        # After adding a new blog post to the database, instead of going
        # back to the main page, we go to that blog post's individual entry
        # page to display the new post.
        return redirect("/blog?id=" + str(id))
    else:
        return render_template('newpost.html',title="New Post",
            title_error=title_error,
            body_error=body_error,
            name=name,
            body=body)


@app.route('/blog/newpost', methods=['GET'])
def getform():

    return render_template('newpost.html',title="New Post")

@app.route('/', methods=['GET'])
def index():
    # Query the user table to create a list of all existing users
    # This list will be rendered on the home page. 

    user_list = User.query.all()

    return render_template('index.html', title="Blog Users!",
        user_list=user_list)


if __name__ == '__main__':
    app.run()