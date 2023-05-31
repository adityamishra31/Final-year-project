from flask.globals import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from project_orm import User, Upload, PasswordResetRequest
from utils import *
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
from flask_mail import Mail, Message
from threading import Thread
from datetime import datetime, timedelta
import uuid
import pandas as pd
from ibcm_csv import *
import visualizer as vis
import plotly.graph_objects as go
import plotly.io as pio


app = Flask(__name__)
app.secret_key = "the basics of life with python"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
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
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return


def get_db():
    engine = create_engine('sqlite:///database.sqlite')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()

def mine(uploaded_file = "Market_Basket_Optimisation.csv", w=3):
    activities = ['A','B','C','D']
    w = 2
    miner = ConstraintMining(uploaded_file, activities, w)
    miner.mine_binaries()
    return miner.local_constraints

def visualize(constraint):
    return vis.visualize_local_constraints(constraint).show()
    

# @app.route('/')
# def index():
#     if session.get('isauth'):
#         username = session.get('name')
#         return render_template('upload.html', title=f'Home|{username}')
#     else:
#         return render_template('landing.html')
    
@app.route('/')
def index():
    return render_template('landing.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and validate_email(email):
            if password and len(password) >= 6:
                try:
                    sess = get_db()
                    user = sess.query(User).filter_by(email=email, password=password).first()
                    if user:
                        session['isauth'] = True
                        session['email'] = user.email
                        session['id'] = user.id
                        session['name'] = user.name
                        session['created_at'] = user.created_at
                        del sess
                        flash('hurray! Login successful.', 'success')
                        return redirect('/upload')
                    else:
                        flash('sorry! Email or password is wrong.', 'danger')
                except Exception as e:
                    flash(e, 'danger')
    return render_template('login.html', title='Login')

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
            flash('name must be more than 3 characters.','danger')
    return render_template('signup.html',title='register')


@app.route('/home',methods=['GET','POST'])
def home():
    if session.get('isauth'):
        username = session.get('name')
        return render_template('upload.html',title=f'Home|{username}')
    else :
         return render_template('login.html')


@app.route('/about')
def about():
    return render_template('about.html',title='About Us')

@app.route('/login/profile')
def profile():
    return render_template('profile.html')



# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file:
#             filename = file.filename
#             data = file.read().decode('utf-8')

#             try:
#                 # Attempt to read the CSV file
#                 df = pd.read_csv(pd.compat.StringIO(data))
                
#                 # Save the file data into the database
#                 csv_file = CSVFile(filename=filename, data=data)
#                 db.session.add(csv_file)
#                 db.session.commit()

#                 return redirect(url_for('display_file', file_id=csv_file.id))
            
#             except pd.errors.ParserError:
#                 return "Error parsing the CSV file. Please check the file format."
        
#         else:
#             return redirect(url_for('upload_form'))






# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


# # Root URL
# @app.route('/')
# def index():
#      # Set The upload HTML template '\templates\index.html'
#     return render_template('\templates\upload.html')


#Get the uploaded files

# @app.route("/", methods=['POST'])
# def uploadFiles():
#       # get the uploaded file
      
#           # save the file
#       return redirect(url_for('upload'))
ALLOWED_EXTENSIONS = {'csv'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
 if session.get('isauth'): 
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
            # flash('Successfully uploaded', 'success')
            df = pd.read_csv(filepath)
            c = mine(filepath,3)
            fig = visualize(c)
           

            return render_template('display.html', data=df.to_html(), c=c, fig=fig.to_html())
        else:
            return redirect(url_for('upload'))

    return render_template('upload.html')


@app.route('/logout')
def logout():
    if session.get('isauth'):
        session.clear()
        flash('you have been logged out','warning')
    return redirect('/login')


# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         uploaded_file = request.files['file']
#         if uploaded_file.filename != '':
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
#           # set the file path
#             uploaded_file.save(file_path)
        
#             df = pd.read_csv(file)
#             c = mine(file)
#             fig = visualize(c)

#             return render_template('display.html', data=df.to_html(), c=c, fig=fig.to_html())
#         else:
#             return redirect(url_for('upload'))
#     else :
#         return render_template('upload.html')    

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
                flash("password did not match",'danger')
                return redirect(url_for('reset_password', token=token))
        else:
            
            return "User not found"
    return render_template('reset_password.html', token=token)

@app.route('/login/button', methods=[' POST '])
def button():
    return render_template('button.html')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
