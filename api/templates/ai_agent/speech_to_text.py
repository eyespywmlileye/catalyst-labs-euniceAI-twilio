import time 
from datetime import datetime

import assemblyai as aai


from api.models.mongo_db import mongodb
from api.config.mongodb_config import MongoDBAtlas

import uuid

import openai
from typing import Annotated
from langchain_core.tools import tool
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
 
from api.templates.ai_agent.agent import Assistant, State
from api.templates.ai_agent.tools.booking import BookingManager
from api.templates.ai_agent.tools.rag import VectorStoreRetriever, load_data
from api.templates.ai_agent.utils import create_tool_node_with_fallback, _print_event

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

    docs = load_data(r"/home/ec2-user/Catalyst-Labs/plumber.txt")

    retriever = VectorStoreRetriever.from_docs(docs, openai.Client())

    @tool
    def lookup_policy(query: str) -> str:
            """Consult the company policies to check whether certain options are permitted.
            Use this before making any booking changes performing other 'write' events.
            You can also get information about FAQs, services offered by the company along with their pricing details and other general information
            """
            docs = retriever.query(query, k=2)
            return "\n\n".join([doc["page_content"] for doc in docs])


    booking_manager = BookingManager("business_bookings.db")


    llm = ChatGroq(model="llama3-groq-70b-8192-tool-use-preview", temperature=0.3)

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful customer support assistant for {company_name}. "
                " Use the provided tools to make and manage a user's bookings, search company services, faqs and policies, and other information to assist the user's queries. "
                " When searching, be persistent. Expand your query bounds if the first search returns no results. "
                " If a search comes up empty, expand your search before giving up."
                "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
                "\nCurrent time: {time}.",
            ),
            ("placeholder", "{messages}"),
        ]
    ).partial(time=datetime.now())

    part_1_tools = [
        TavilySearchResults(max_results=1),
        lookup_policy,
        booking_manager.fetch_user_bookings,
        booking_manager.create_booking,
        booking_manager.update_booking_status,
        booking_manager.update_booking_date,
        booking_manager.update_booking_service,
        booking_manager.cancel_booking,
    ]
    part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(part_1_tools)

    builder = StateGraph(State)


    # Define nodes: these do the work
    builder.add_node("assistant", Assistant(part_1_assistant_runnable))
    builder.add_node("tools", create_tool_node_with_fallback(part_1_tools))
    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    # The checkpointer lets the graph persist its state
    # this is a complete memory for the entire graph.
    memory = SqliteSaver.from_conn_string(":memory:")
    part_1_graph = builder.compile(checkpointer=memory)



    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            # The passenger_id is used in our flight tools to
            # fetch the user's flight information
            "booking_id": 2,
            "company_name": "Bob the Builder Warehouses",
            # Checkpoints are accessed by thread_id
            "thread_id": thread_id,
        }
    }

    _printed = set()
 
    start = time.time()
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        print(transcript.text, end="\r\n")
        
        # TODO: Implement a Query Model (llm) to process the transcript

        while True:
            question = transcript.text
            if question == "exit":
                break
            events = part_1_graph.invoke(
                {"messages": ("user", question)}, config, stream_mode="values"
            )
            
            output_text = events.get("messages")[-1].content
        
            
            
            # Save the transcript to the database
            mongodb.cx[mongodb_atlas.database_name][mongodb_atlas.usage_metrics_collection].insert_one({
                'text': transcript.text, 
                "response": output_text, 
                "processing_time": time.time() - start,  
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