from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from threading import Thread
import time
import os 

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

stringg = "mongodb+srv://bot:SJMm1LUcA5voLeWN@cluster0.rxbs3g5.mongodb.net/"
print(stringg)
# MongoDB client setup
client = MongoClient(stringg)
db = client['ai_call_centre']
collection = db['test']


import os
import requests
from dotenv import load_dotenv
import subprocess
import shutil
import time
from deepgram import Deepgram

# brew install portaudio

# Load environment variables
load_dotenv()

 
class TextToSpeech:
    # Set your Deepgram API Key and desired voice model
    DG_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    MODEL_NAME = "aura-helios-en"  # Example model name, change as needed

    @staticmethod
    def is_installed(lib_name: str) -> bool:
        lib = shutil.which(lib_name)
        return lib is not None

    def speak(self, text):
        if not self.is_installed("ffplay"):
            raise ValueError("ffplay not found, necessary to stream audio.")

        DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={self.MODEL_NAME}&performance=some&encoding=linear16&sample_rate=24000"
        headers = {
            "Authorization": f"Token {self.DG_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text
        }

        player_command = ["ffplay", "-autoexit", "-", "-nodisp"]
        player_process = subprocess.Popen(
            player_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        start_time = time.time()  # Record the time before sending the request
        first_byte_time = None  # Initialize a variable to store the time when the first byte is received

        with requests.post(DEEPGRAM_URL, stream=True, headers=headers, json=payload) as r:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    if first_byte_time is None:  # Check if this is the first chunk received
                        first_byte_time = time.time()  # Record the time when the first byte is received
                        ttfb = int((first_byte_time - start_time)*1000)  # Calculate the time to first byte
                        print(f"TTS Time to First Byte (TTFB): {ttfb}ms\n")
        
                    player_process.stdin.write(chunk)
                    player_process.stdin.flush()

        if player_process.stdin:
            player_process.stdin.close()
        player_process.wait()
        
 
# Function to handle change stream
def monitor_changes():
    print("Starting to monitor changes...")
    with collection.watch() as stream:
        for change in stream:
            print(change)
            print(change.keys())
            print("Change detected: %s", change)
            TextToSpeech().speak(change['fullDocument']['text'])
            
            
if __name__ == '__main__':
    # Start the change stream monitoring in a separate thread
    try:
        thread = Thread(target=monitor_changes)
        thread.start()
        print("Thread started.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        # Close the MongoDB client connection and clean up
        print("Cleaning up...")
        collection.delete_many({})
        print("All documents deleted.")
        thread.join()
        print("Thread joined. Exiting.")