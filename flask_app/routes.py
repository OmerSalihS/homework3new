# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for
from flask_socketio import emit, join_room, leave_room
from .utils.database.database  import database
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
	return session.get('name', 'Unknown')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/logout')
def logout():
	# Clear all session data
	session.clear()
	return redirect('/')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
	email = form_fields['email']
	password = form_fields['password']
	
	# Authenticate the user
	auth_result = db.authenticate(email=email, password=password)
	
	if auth_result['success'] == 1:
		# Store the encrypted email and name in the session
		session['email'] = db.reversibleEncrypt('encrypt', email)
		session['name'] = auth_result['name']
		session['role'] = auth_result['role']
		
		# Reset failed login attempts counter
		session['failed_attempts'] = 0
		
		# Check if there's a next parameter for redirect
		next_url = request.args.get('next')
		if next_url and next_url.startswith('/'):
			return json.dumps({'success': 1, 'redirect': next_url})
		return json.dumps({'success': 1, 'redirect': '/home'})
	else:
		# Increment failed login attempts counter
		failed_attempts = session.get('failed_attempts', 0) + 1
		session['failed_attempts'] = failed_attempts
		
		# Authentication failed
		return json.dumps({
			'success': 0, 
			'message': auth_result['message'],
			'failed_attempts': failed_attempts
		})


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    user = getUser()
    is_owner = session.get('role') == 'owner'
    role = "Owner" if is_owner else "Guest"
    emit('status', {'msg': f"{user} ({role}) has entered the room.", 'class': 'system-message'}, room='main')

@socketio.on('left', namespace='/chat')
def left(message):
    user = getUser()
    is_owner = session.get('role') == 'owner'
    role = "Owner" if is_owner else "Guest"
    emit('status', {'msg': f"{user} ({role}) has left the room.", 'class': 'system-message'}, room='main')
    leave_room('main')

@socketio.on('message', namespace='/chat')
def handle_message(message):
    user = getUser()
    is_owner = session.get('role') == 'owner'
    role = "Owner" if is_owner else "Guest"
    
    # Determine message class based on user role
    msg_class = 'owner-message' if is_owner else 'user-message'
    
    # Format the message with the user's name and role
    formatted_msg = f"{user} ({role}): {message['msg']}"
    
    # Emit the message to all users in the room
    emit('status', {'msg': formatted_msg, 'class': msg_class}, room='main')

#######################################################################################
# OTHER
#######################################################################################

@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	x = random.choice(['I started university when I was a wee lad of 15 years.','I have a pet sparrow.','I write poetry.'])
	return render_template('home.html', fun_fact = x)

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	pprint(resume_data)
	return render_template('resume.html', resume_data = resume_data)

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/piano')
def piano():
    return render_template('piano.html')

@app.route('/processfeedback', methods=['POST'])
def processfeedback():
    # Access the form data
    feedback = request.form
    
    # Extract the data
    name = feedback.get('name')
    email = feedback.get('email')
    comment = feedback.get('comment')
    
    # Insert the feedback into the database
    columns = ['name', 'email', 'comment']
    parameters = [[name, email, comment]]
    db.insertRows(table='feedback', columns=columns, parameters=parameters)
    
    # Retrieve all feedback from the database
    feedback_query = "SELECT * FROM feedback ORDER BY comment_id DESC"
    all_feedback = db.query(feedback_query)
    
    # Render the feedback template with all feedback data
    return render_template('processfeedback.html', feedback_data=all_feedback)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/processregister', methods=["POST", "GET"])
def processregister():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    email = form_fields['email']
    password = form_fields['password']
    role = form_fields['role']
    name = form_fields['name']
    
    # Create the user
    result = db.createUser(email=email, password=password, role=role, name=name)
    
    return json.dumps(result)