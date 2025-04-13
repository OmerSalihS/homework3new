# Author: Prof. MM Ghassemi <ghassem3@msu.edu>

#--------------------------------------------------
# Import Requirements
#--------------------------------------------------
import os
from flask import Flask
from flask_socketio import SocketIO
from flask_failsafe import failsafe

socketio = SocketIO(cors_allowed_origins="*")

#--------------------------------------------------
# Create a Failsafe Web Application
#--------------------------------------------------
@failsafe
def create_app(debug=False):
	app = Flask(__name__)

	# Configure the application
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.debug = debug
	app.secret_key = os.environ.get('SECRET_KEY', 'AKWNF1231082fksejfOSEHFOISEHF24142124124124124iesfhsoijsopdjf')

	# Initialize database
	from .utils.database.database import database
	db = database()
	
	# Only create tables if they don't exist
	try:
		db.createTables(purge=False)
		
		# Create test users only if they don't exist
		try:
			db.createUser(email='owner@email.com', password='password', role='owner', name='Owner')
		except:
			pass  # User might already exist
			
		try:
			db.createUser(email='guest@email.com', password='password', role='guest', name='Guest')
		except:
			pass  # User might already exist
	except Exception as e:
		app.logger.error(f"Database initialization error: {str(e)}")
		# Continue without database - will show error page

	socketio.init_app(app)

	with app.app_context():
		from . import routes
		return app
