from flask.globals import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from project_orm import User, Upload,PasswordResetRequest
from utils import *
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
from flask_mail import Mail, Message
from threading import Thread
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = "the basics of life with python"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/static/uploads'
app.config['MAIL_SERVER'] = 'mail.digipodium.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "adityakumarmishra5066@digipodium.com"
app.config['MAIL_PASSWORD'] = "digipodium50662k22"
mail = Mail(app)



def session_add(key, value):
    session[key] = value


def save_file(file):
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'][1:], filename)
    file.save(path)
    return 

def get_db():
    engine = create_engine('sqlite:///database.sqlite')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and validate_email(email):
            if password and len(password)>=6:
                try:
                    sess = get_db()
                    user = sess.query(User).filter_by(email=email,password=password).first()
                    if user:
                        session['isauth'] = True
                        session['email'] = user.email
                        session['id'] = user.id
                        session['name'] = user.name
                        session['created_at']=user.created_at
                        del sess
                        flash('hurray! Login successfull.','success')
                        return redirect('/home')
                    else:
                        flash('sorry!email or password is wrong.','danger')
                except Exception as e:
                    flash(e,'danger')
    return render_template('index.html',title='login')

@app.route('/signup',methods=['GET','POST'])
def signup():
   
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if name and len(name) >= 3:
            if email and validate_email(email):
                if password and len(password)>=6:
                    if cpassword and cpassword == password:
                        try:
                            sess = get_db()
                            newuser = User(name=name,email=email,password=password)
                            sess.add(newuser)
                            sess.commit()
                            del sess
                            flash('hurray!registration successful.','success')
                            return redirect('/')
                        except:
                            flash('*email account already exists','danger')
                    else:
                        flash('*Sorry!confirm password does not match','danger')
                else:
                    flash('*password must be of more than 6 characters.','danger')
            else:
                flash('*invalid email!','danger')
        else:
            flash('*invalid name! must be more than 3 characters.','danger')
    return render_template('signup.html',title='register')


@app.route('/home',methods=['GET','POST'])
def home():
    if session.get('isauth'):
        username = session.get('name')
        return render_template('upload.html',title=f'Home|{username}')
    else :
         return render_template('home.html')
   

@app.route('/about')
def about():
    return render_template('about.html',title='About Us')

@app.route('/login/profile')
def profile():
    return render_template('/profile.html')

@app.route('/logout')
def logout():
    if session.get('isauth'):
        session.clear()
        flash('you have been logged out','warning')
    return redirect('/login')



app.config['UPLOAD_FOLDER'] = 'static/uploads'

ALLOWED_EXTENSIONS = {'csv','txt','.xlsx'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part        
        name = request.form.get('name')
        file = request.files.get('file')
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if name == '' :
           name = secure_filename(file.filename)[:15]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = app.config['UPLOAD_FOLDER']+filename 
            file.save(filepath)
            session['last_upload'] = filepath
            file_size = os.stat(filepath).st_size
            size_mb = round(file_size / (1024 * 1024), 1)
            size_mb_str = f"{size_mb} MB"
            db = get_db()
            db.add(Upload(name=name, path=filepath, size=size_mb_str))
            db.commit()
            db.close()
            flash('Successfully uploaded', 'success')
            return redirect('/upload')
    return render_template('upload.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/history')
def history():
    if session['isauth']:
        db = get_db()
        files = db.query(Upload).filter(Upload.added_by==session.get('id'))
        return render_template('history.html', files = files)
    else:
        flash('Please login before accessing')
        return redirect('/login')


        


@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        sess = get_db()
        user = sess.query(User).filter_by(email=email).first()
        if user:
            token = str(uuid.uuid4())
            expiration_date = datetime.now() + timedelta(hours=1)
            db = get_db()
            reset_request = PasswordResetRequest(email=email, token=token, expiration_date=expiration_date)
            db.add(reset_request)
            db.commit()
            reset_link = url_for('reset_password',token=token, _external=True)
            # Send an email containing the reset_link to the user
            def send_email(app, msg):
                with app.app_context():
                         mail.send(msg)
            Email_body=f' this is {reset_link} for password reset'
            msg =Message()
            msg.subject = "Password Reset Request"
            
            msg.recipients = [email]
            msg.sender = 'adityakumarmishra5066@digipodium.com'
            msg.body = Email_body
            Thread(target=send_email, args=(app, msg)).start()
            
            return 'Email sent successfully'
        else:
            flash('Sorry! You are not registered', 'danger')
            return redirect('/forgot')
    return render_template('forgot.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    sess=get_db()
    reset_request = sess.query(PasswordResetRequest).filter_by(token=token).first()
    if not reset_request or reset_request.expiration_date < datetime.now():
        return "Invalid or expired token"
    if request.method == 'POST':
        user = sess.query(User).filter_by(email=reset_request.email).first()
        if user:
            user.password = request.form['password']
            cpassword=request.form['cpassword']
            if cpassword == user.password:
                    
                    sess.delete(reset_request)
                    sess.commit()
                    sess.close()
                    return "Password reset successful"
        else:
            
            return "User not found"
    return render_template('reset_password.html', token=token)


if __name__ == "__main__":
    app.run(debug=True,threaded=True)


