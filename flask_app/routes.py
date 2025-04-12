# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, jsonify, flash
from flask_socketio import emit, join_room, leave_room
from flask_login import login_user, logout_user, login_required, current_user
from .utils.database.database import createUser, authenticate, saveChatMessage, getChatMessages
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
import logging
from . import socketio, db
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

db = database()

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def getUser():
    if 'email' in session:
        return session['email']
    return 'Unknown'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/processlogin', methods=['POST'])
def processlogin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    result = authenticate(email, password)
    if result['success']:
        session['user_id'] = result['user']['id']
        session['email'] = result['user']['email']
        session['name'] = result['user']['name']
        session['role'] = result['user']['role']
    return jsonify(result)

#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
def chat():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html')

@socketio.on('join')
def on_join():
    if 'email' in session:
        join_room('chat')
        emit('status', {'msg': f"{session['email']} has entered the room."}, room='chat')
        # Load previous messages
        messages = getChatMessages()
        for msg in messages:
            emit('message', {
                'user': msg['user'],
                'message': msg['message'],
                'role': msg['role'],
                'timestamp': msg['timestamp']
            }, room='chat')

@socketio.on('leave')
def on_leave():
    if 'email' in session:
        leave_room('chat')
        emit('status', {'msg': f"{session['email']} has left the room."}, room='chat')

@socketio.on('message')
def handle_message(data):
    if 'email' in session:
        user = session['email']
        role = session.get('role', 'user')
        message = data.get('message', '')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save message to database
        saveChatMessage(user, message, role)
        
        # Emit message to all users in the room
        emit('message', {
            'user': user,
            'message': message,
            'role': role,
            'timestamp': timestamp
        }, room='chat')

#######################################################################################
# OTHER
#######################################################################################

@app.route('/home')
def home():
	x = random.choice(['I started university when I was a wee lad of 15 years.','I have a pet sparrow.','I write poetry.'])
	return render_template('home.html', fun_fact = x)

@app.route('/resume')
def resume():
	try:
		resume_data = db.getResumeData()
		pprint(resume_data)
		return render_template('resume.html', resume_data = resume_data)
	except Exception as e:
		logger.error(f"Error in resume route: {str(e)}")
		return render_template('resume.html', resume_data = [])

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/piano')
def piano():
    return render_template('piano.html')

@app.route('/processfeedback', methods=['POST'])
def processfeedback():
    try:
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
    except Exception as e:
        logger.error(f"Error in processfeedback route: {str(e)}")
        return render_template('processfeedback.html', feedback_data=[])

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/processregister', methods=['POST'])
def processregister():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'user')
    
    success, message = createUser(email, password, name, role)
    return jsonify({'success': success, 'message': message})