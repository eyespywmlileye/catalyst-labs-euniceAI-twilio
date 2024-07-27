import os
import time
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder,  SystemMessagePromptTemplate, HumanMessagePromptTemplate

from src.models.prompt_templates import conversation_agent_prompt


load_dotenv()

class GroqLlm(): 
    def __init__(self):
        self.groq = ChatGroq(
            temperature = 0, 
            model_name = 'mixtral-8x7b-32768',
            groq_api_key = os.getenv('GROQ_API_KEY')
        )
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        system_prompt = conversation_agent_prompt()
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{text}")
        ])

        self.conversation = LLMChain(
            llm=self.groq,
            prompt=self.prompt,
            memory=self.memory
        )

    def process(self, text):
        self.memory.chat_memory.add_user_message(text)  # Add user message to memory

        start_time = time.time()

        # Go get the response from the LLM
        response = self.conversation.invoke({"text": text})
        end_time = time.time()

        self.memory.chat_memory.add_ai_message(response['text'])  # Add AI response to memory

        elapsed_time = int((end_time - start_time) * 1000)
        return response['text']

if __name__ == "__main__": 
    llm_conversation = GroqLlm()
    llm_conversation.process("Hello, how are you?")
    