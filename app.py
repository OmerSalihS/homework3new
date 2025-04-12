import os
import logging
from flask_app import create_app, socketio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
	logger.info("Creating Flask application")
	app = create_app(debug=True)
	logger.info("Flask application created successfully")
except Exception as e:
	logger.error(f"Error creating Flask application: {str(e)}")
	raise

if __name__ == "__main__":
	try:
		port = int(os.environ.get("PORT", 8080))
		logger.info(f"Starting application on port {port}")
		socketio.run(app, host='0.0.0.0', port=port)
	except Exception as e:
		logger.error(f"Error running application: {str(e)}")
		raise