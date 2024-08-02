import time 
from datetime import datetime

import assemblyai as aai


from api.models.mongo_db import mongodb
from api.config.mongodb_config import MongoDBAtlas


from dotenv import load_dotenv 

load_dotenv()

mongodb_atlas = MongoDBAtlas()

# Sample rate for Twilio audio streams
TWILIO_SAMPLE_RATE: int = 8000  # 8 kHz
 
def on_open(session_opened: aai.RealtimeSessionOpened):
    """
    Callback function called when a realtime session is opened.
    
    Args:
        session_opened (aai.RealtimeSessionOpened): The session opened event object.
    """
    print("Session ID:", session_opened.session_id)


def on_data(transcript: aai.RealtimeTranscript):
    """
    Process the given transcript and print the text.

    Args:
        transcript (aai.RealtimeTranscript): The transcript to process.

    Returns:
        None
    """
    
    start = time.time()
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        print(transcript.text, end="\r\n")
        
        # TODO: Implement a Query Model (llm) to process the transcript
        # Query Model llm model
        llm = ""
        
        # Save the transcript to the database
        mongodb.cx[mongodb_atlas.database_name][mongodb_atlas.usage_metrics_collection].insert_one({
            'text': transcript.text, 
            "response": llm, 
            "processing_time": time.time() - start, 
            "session_id": on_open.session_opened.session_id, 
            "dateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    else:
        print(transcript.text, end="\r")
 
 
def on_error(error: aai.RealtimeError) :
    """
    Callback function to handle errors that occur during real-time speech-to-text processing.

    Parameters:
    error (aai.RealtimeError): The error that occurred.

    Returns:
    None
    """
    
    print("An error occurred:", error)


def on_close():
    """
    This function is called when the session is being closed.
    It prints a message indicating that the session is closing.
    """
    print("Closing Session")


class TwilioTranscriberClass(aai.RealtimeTranscriber):
    def __init__(self): 
        super().__init__(
            on_data=on_data,
            on_error=on_error,
            on_open=on_open, 
            on_close=on_close, 
            sample_rate=TWILIO_SAMPLE_RATE,
            encoding=aai.AudioEncoding.pcm_mulaw
        )