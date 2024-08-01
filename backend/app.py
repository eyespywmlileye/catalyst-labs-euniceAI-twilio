import os 
import boto3

from dotenv import load_dotenv
from flask import Flask, request , jsonify, render_template 
from src.models.llm import GroqLlm
from src.models.speech_to_text import get_transcript
from src.models.text_to_speech import TextToSpeech
class ConversationManager:
    def __init__(self):
        self.transcription_response = ""
        self.llm = GroqLlm()

    async def main(self):
        def handle_full_sentence(full_sentence):
            self.transcription_response = full_sentence

        # Loop indefinitely until "goodbye" is detected
        while True:
            await get_transcript(handle_full_sentence)
            
            # Check for "goodbye" to exit the loop
            if "goodbye" in self.transcription_response.lower():
                break
            
            llm_response = self.llm.process(self.transcription_response)
            print(llm_response)
            
            # Reset transcription_response for the next loop iteration
            self.transcription_response = ""
            
            tts = TextToSpeech()
            tts.speak(llm_response)
            
            
app = Flask(__name__)



# render html
@app.route("/")
def index():
    return render_template("index.html")


# function to transcript audio using whisper
@app.route("/process-audio", methods=["POST"])
def process_audio_data():
    
    audio_data = request.files["audio"].read()

    print("Processing audio...")
    # Create a temporary file to save the audio data
    try:
        output =  "5"

        print(output)
        results = output["text"]

        return jsonify({"transcript": results})
    except Exception as e:
        print(f"Error running Replicate model: {e}")
        return jsonify({"error": str(e)}), 500