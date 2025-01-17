import json
import base64  # decode incoming audio stream
from datetime import datetime

from flask_sock import Sock
from flask import request, Response, Blueprint

from api.models.websocket import sock
from api.models.mongo_db import mongodb
from api.config.mongodb_config import MongoDBAtlas

from api.templates.ai_agent.speech_to_text import TwilioTranscriberClass

from dotenv import load_dotenv

load_dotenv()

INCOMING_CALL_ROUTE = '/'
WEBSOCKET_ROUTE: str = '/jeffrey_init'

mongodb_atlas = MongoDBAtlas()

ai_agent = Blueprint(name='ai_agent',
                     import_name=__name__,
                     url_prefix='/api/v1/ai_agent')
 
@sock.route(WEBSOCKET_ROUTE)
def transcription_websocket(ws):
    
 
    transcriber = None
    while True:
        data = json.loads(ws.receive())
        match data['event']:
            case "connected":
                transcriber = TwilioTranscriberClass()
                transcriber.connect()

                # update the current state to connected
                mongodb.cx[mongodb_atlas.database_name][mongodb_atlas.state_manager_collection].update_one(
                    {'name': "state_manager"},
                    {'$set': {'state': 'connected',
                              "dateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
                    upsert=True
                )
                print('transcriber connected')

            case "start":
                print('twilio started')

            case "media":
                if transcriber:
                    # Decode the incoming audio stream
                    payload_b64: str = data['media']['payload']
                    # Decode the base64 encoded audio stream
                    payload_mulaw: bytes = base64.b64decode(payload_b64)
                    # Stream the audio to the transcriber
                    transcriber.stream(payload_mulaw)

            case "stop":
                if transcriber:
                    print('twilio stopped')
                    transcriber.close()
                    # update the current state to closed
                    mongodb.cx[mongodb_atlas.database_name][mongodb_atlas.state_manager_collection].update_one(
                        {'name': "state_manager"},
                        {'$set': {'state': 'closed',
                                  "dateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
                    )
                    print('transcriber closed')