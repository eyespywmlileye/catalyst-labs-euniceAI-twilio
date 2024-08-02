import os 
from typing import Dict , List

import assemblyai as aai

from flask_cors import CORS
from flask import Flask, jsonify 

from api.v1.models.mongo_db import mongodb

from api.v1.templates.ai_agent.ai_agent_api import ai_agent
from api.v1.templates.knowledge_base.pinecone_api import pincone_blueprint
from api.v1.templates.knowledge_base.object_store_api import aws_object_store

from dotenv import load_dotenv
load_dotenv()

def create_app(test_config: Dict[str ,str] = None) -> Flask:

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
        )
        
        # ngrok auth 
        ngrok.set_auth_token(os.environ['NGROK_AUTH_TOKEN'])

        # Assembly AI 
        aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')
        

    elif test_config is not None:
        app.config.from_mapping(test_config)
         
    # Register PyMongo DB --> MonogDB 
    mongodb.app = app # set the app instance for the PyMongo DB ( we imported is from our mongodb from src/models/mongodb_database.py)
    mongodb.init_app(app) # use the app.config MONGO_URI that was initialized above

    
    # Register Blueprints 
    app.register_blueprint(ai_agent)
    app.register_blueprint(pincone_blueprint) 
    app.register_blueprint(aws_object_store)
    
    # Home Route 
    @app.route('/api/v1/home', methods=['GET'])
    def home():
        return jsonify({"message": "Welcome to Catalyst Labs API"}), 200
    
    return app