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
    return vis.visualize_local_constraints(miner.local_constraints)

@app.route('/')
def index():
    if session.get('isauth'):
        username = session.get('name')
        return render_template('upload.html', title=f'Home|{username}')
    else:
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
                        return redirect('/home')
                    else:
                        flash('sorry! Email or password is wrong.', 'danger')
                except Exception as e:
                    flash(e, 'danger')
    return render_template('index.html', title='Login')

# enable debugging mode
app.config["DEBUG"] = True


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

@app.route("/", methods=['POST'])
def uploadFiles():
      # get the uploaded file
      uploaded_file = request.files['file']
      if uploaded_file.filename != '':
           file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
          # set the file path
           uploaded_file.save(file_path)
          # save the file
      return redirect(url_for('upload'))




@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_csv(file)
            c = mine(file)
            fig = visualize(c)

            return render_template('display.html', data=df.to_html(), c=c, fig=fig.to_html())
        else:
            return redirect(url_for('upload'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
