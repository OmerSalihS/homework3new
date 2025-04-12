# Author: Prof. MM Ghassemi <ghassem3@msu.edu>

#--------------------------------------------------
# Import Requirements
#--------------------------------------------------
import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_failsafe import failsafe
from flask_login import LoginManager
from .utils.database.sqlite_database import SQLiteDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Initialize SocketIO
socketio = SocketIO(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize database
db = SQLiteDatabase()

# Create test users if they don't exist
def create_test_users():
	try:
		# Create owner user
		db.createUser(
			email='owner@example.com',
			password='owner123',
			name='Owner User',
			role='owner'
		)
		
		# Create guest user
		db.createUser(
			email='guest@example.com',
			password='guest123',
			name='Guest User',
			role='user'
		)
		
		logger.info("Test users created successfully")
	except Exception as e:
		logger.error(f"Error creating test users: {str(e)}")

# Create test users when the app starts
create_test_users()

#--------------------------------------------------
# Create a Failsafe Web Application
#--------------------------------------------------
@failsafe
def create_app(debug=False):
	try:
		app = Flask(__name__)
		logger.info("Flask application created")

		# NEW IN HOMEWORK 3 ----------------------------
		# This will prevent issues with cached static files
		app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
		app.debug = debug
		# The secret key is used to cryptographically-sign the cookies used for storing the session data.
		app.secret_key = 'AKWNF1231082fksejfOSEHFOISEHF24142124124124124iesfhsoijsopdjf'
		# ----------------------------------------------

		from .utils.database.database import database
		db = database()
		logger.info("Database initialized")
		
		try:
			db.createTables(purge=True)
			logger.info("Database tables created")
		except Exception as e:
			logger.error(f"Error creating database tables: {str(e)}")
		
		# NEW IN HOMEWORK 3 ----------------------------
		# This will create a user
		try:
			db.createUser(email='owner@email.com', password='password', role='owner', name='Owner')
			db.createUser(email='guest@email.com', password='password', role='guest', name='Guest')
			logger.info("Test users created")
		except Exception as e:
			logger.error(f"Error creating test users: {str(e)}")
		# ----------------------------------------------

		# Initialize SocketIO with the app
		socketio.init_app(app, message_queue=None)
		logger.info("SocketIO initialized")

		with app.app_context():
			from . import routes
			logger.info("Routes imported")
			return app
	except Exception as e:
		logger.error(f"Error creating application: {str(e)}")
		raise

# Register error handlers
@app.errorhandler(404)
def not_found_error(error):
	logger.error(f"404 error: {error}")
	return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
	logger.error(f"500 error: {error}")
	return "Internal server error", 500

if __name__ == '__main__':
	socketio.run(app, debug=True, host='0.0.0.0', port=8080)
