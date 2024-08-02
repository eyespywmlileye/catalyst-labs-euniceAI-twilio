import os 

import ngrok 
from twilio.rest import Client

from api_config.__init__ import create_app
from api.templates.ai_agent.ai_agent_api import INCOMING_CALL_ROUTE

from dotenv import load_dotenv
load_dotenv()


def init_twilio_ngrok(port: str)-> None:  
    """
    Initializes Twilio integration with Ngrok tunneling.
    
    This function sets up the necessary configurations for Twilio integration with Ngrok tunneling.
    It retrieves the Twilio account credentials from environment variables, creates a Twilio client,
    opens an Ngrok tunnel, and sets the Ngrok URL as the webhook for the specified Twilio number.
    
    Args:
    - port: The port number for the Flask application.
    
    """
    
    # Twilio AUTH
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    api_key = os.environ['TWILIO_API_KEY_SID']
    api_secret = os.environ['TWILIO_API_SECRET']

    # Create a Twilio client
    client = Client(api_key, api_secret,account_sid)

    # Twilio Number 
    TWILIO_NUMBER = os.environ['TWILIO_NUMBER']
    
    try: 
        # Open Ngrok tunnel
        listener = ngrok.forward(f"http://localhost:{port}")
        print(f"Ngrok tunnel opened at {listener.url()} for port {port}")
        NGROK_URL = listener.url()
 
            
        # Set ngrok URL to be the webhook for the appropriate Twilio number
        twilio_nums = client.incoming_phone_numbers.list()
        twilio_num_sid = [twl_number.sid for twl_number in twilio_nums if twl_number.phone_number == TWILIO_NUMBER][0]
        
        
        client.incoming_phone_numbers(twilio_num_sid).update(account_sid, 
                                                            voice_url=f"{NGROK_URL}{INCOMING_CALL_ROUTE}")
    except Exception as e: 
        print(f"Error setting up Twilio Ngrok tunnel: {e}")
        return None
    
app = create_app()
if __name__ == "__main__":
    
        
    PORT: str = '5000'
    DEBUG: bool = False
        
    try:    
        # Initialize Twilio integration with Ngrok tunneling
        init_twilio_ngrok(port = PORT)
        
        
        app.run(port = PORT,
                debug=DEBUG)
        
    finally: 
        # Disconnect Ngrok tunnel
        ngrok.disconnect()