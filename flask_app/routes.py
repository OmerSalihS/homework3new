# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request
from .utils.database.database  import database
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
db = database()

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