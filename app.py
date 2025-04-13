import os
from flask_app import create_app, socketio

app = create_app(debug=False)  # Set debug to False for production
if __name__ == "__main__":
	port = int(os.environ.get("PORT", 8080))
	socketio.run(app, host='0.0.0.0', port=port)