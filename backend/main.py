import asyncio

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
            
if __name__ == "__main__":
    manager = ConversationManager()
    asyncio.run(manager.main())