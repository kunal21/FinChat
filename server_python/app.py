from flask import Flask, request
import os
from flask_cors import CORS 
from db import init_db
from routes import blueprints
import logging
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3001")
    CORS(
        app,
        resources={r"/*": {"origins": frontend_origin}},  # all routes
        supports_credentials=True        # if you need cookies / auth headers
    )

    # Configure logging to filter out watchdog logs
    logging.getLogger('watchdog').setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    app.logger.info("Starting Flask application")
    init_db(app)

    from models import (
        TimestampMixin,                 
        User,
        Item,
        Asset,
        Account,
        Transaction,
        LinkEvent,
        PlaidApiEvent,
        create_timestamp_trigger,
        create_database_views,
        TransactionView,
        AccountView
    )

    # Initialize Socket.IO with proper configuration
    socketio = SocketIO(
        app,
        cors_allowed_origins=frontend_origin,
        logger=True,
        engineio_logger=True
    )

    # Add connection event handlers
    @socketio.on('connect')
    def handle_connect():
        app.logger.info('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        app.logger.info('Client disconnected')

    for bp in blueprints:                
        app.register_blueprint(bp)

    # Store socket.io instance in app config
    app.config['socketio'] = socketio

    return app

app = create_app()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    socketio = app.config['socketio']
    socketio.run(app, host="0.0.0.0", port=port, debug=True, use_reloader=True, allow_unsafe_werkzeug=True)