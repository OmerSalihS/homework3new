import os
from flask_app import create_app, socketio

app = create_app(debug=True)

if __name__ == "__main__":
	# For local development
	socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
else:
	# For production (Cloud Run)
	# This is needed for Cloud Run
	from flask import Flask
	from flask_socketio import SocketIO
	
	# Create a new SocketIO instance for production
	socketio = SocketIO(app, cors_allowed_origins="*")
	
	# Initialize the app with the socketio instance
	socketio.init_app(app)