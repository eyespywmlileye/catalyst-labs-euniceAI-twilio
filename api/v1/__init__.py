import os 
from typing import Dict , List

from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from api.v1.models.mongo_db import mongodb

load_dotenv()

def create_app(test_config: Dict[str ,str] = None):

    app = Flask(__name__, 
                instance_relative_config=True) # Tell flask to look for the instance folder for config files

    # Config CORS 
    allowed_orgins: List[str] = [] # Add allowed origins here
    if not bool(allowed_orgins): 
        allowed_orgins = "*"
        
    # Add CORS origin to restrict access to the API to only the allowed origins
    CORS(app , resources={r'/api/*': {"origins": allowed_orgins}})


    if test_config is None: 
        
        # Config Flask Application
        
        app.config.from_mapping(
            SECRET_KEY = os.environ.get('FLASK_SECRET_KEY'),
            MONGO_URI = os.environ.get('MONGO_URI'),
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY"),
        )

    elif test_config is not None:
        app.config.from_mapping(test_config)
         
    # Register PyMongo DB --> MonogDB 
    mongodb.app = app # set the app instance for the PyMongo DB ( we imported is from our mongodb from src/models/mongodb_database.py)
    mongodb.init_app(app) # use the app.config MONGO_URI that was initialized above
    
    # Config JWT Manager which holds JWT Settigns like access token expiry time, refresh token expiry time (Callbacks for token revokation)
    JWTManager(app) 
    
    # Register Blueprints 
    # app.register_blueprint(auth) 


    @app.route('/api/v1/home', methods=['GET'])
    def home():
        return jsonify({"message": "Welcome to Catalyst Labs API"}), 200
    
    return app