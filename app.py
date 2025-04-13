import os
from flask_app import create_app, socketio

# Set debug to False for production
app = create_app(debug=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Use host 0.0.0.0 to make the application accessible externally
    socketio.run(app, host='0.0.0.0', port=port)
else:
    # This is important for the gunicorn worker to find the app object
    # Gunicorn needs this variable defined at the module level
    gunicorn_app = app