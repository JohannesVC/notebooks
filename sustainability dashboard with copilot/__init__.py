from flask import Flask
import json
import logging
from flask_cors import CORS
import os
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from utils.jwt_config import custom_jwt_required
from utils.limiter_config import limiter

env = os.getenv('FLASK_ENV', 'production')

if env == 'production':
    BASE = 'https://supernova-py-ns7tccoxeq-ew.a.run.app'
    print("BASE = 'CLOUD RUN' \nLOGGER = 'CLOUD LOGGING'")
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client)
    logging.getLogger().setLevel(logging.INFO)  # Set the log level
    logging.getLogger().addHandler(handler)
else:
    BASE = "http://localhost:5000"
    print("BASE = 'http://localhost:5000' \nLOGGER = 'werkzeug'")
    logging.basicConfig(level=logging.INFO)
              
              
def create_app():
    app = Flask('api_orion', static_folder="static")
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {"origins": ["https://orion.supernova.ai",
                            "https://supernova-pe-qqrxdzseoa-lz.a.run.app",
                            "https://supernova-pe-qqrxdzseoa-uc.a.run.app",
                            "http://localhost:80", "http://localhost:5000", 
                            "http://127.0.0.1:5000"],
                    # "allow_headers": ["Content-Type", "Authorization", "Accept"],
                    "methods": ["POST", "GET", "OPTIONS"]}})
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['HOST'] = '0.0.0.0'
    app.config['PORT'] = int(os.environ.get("PORT", 8080))
    
    limiter.init_app(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
        return response
    
    from . import api_v1
    app.register_blueprint(api_v1.bp)
    from api_orion.swagger_setup import init_swagger_ui
    
    init_swagger_ui(app)
    
    return app

# conda activate supernova
# cd C:/Users/johan/Documents/GitHub/supernova-py/
# flask --app api_orion run --debug