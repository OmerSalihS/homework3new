# Author: Prof. MM Ghassemi <ghassem3@msu.edu>

#--------------------------------------------------
# Import Requirements
#--------------------------------------------------
import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_failsafe import failsafe

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SocketIO with async_mode set to eventlet
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet', logger=True, engineio_logger=True)

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
