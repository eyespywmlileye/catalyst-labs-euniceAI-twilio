﻿# Catalyst-Labs

# Setup

## Configure Environment (Conda or Venv)

1. Conda
```
#Create conda environment 

conda create -n <environment name> python=3.10 -y 

# Activate conda environment 
conda activate <environment name>

```

## Pip install requirements 

```
pip install -r requirements.txt
```

## Setup ENV variables 
```
GROQ_API_KEY = <key>
DEEPGRAM_API_KEY = <key>
OPENAI_API_KEY =<key>
MONGO_URI = <uri>
FLASK_SECRET_KEY = <ENTER RANDOM STRING>
PINECONE_API_KEY = <key>
NGROK_AUTH_TOKEN = <key>
TWILIO_API_KEY_SID =<key>
TWILIO_API_SECRET= <key>
TWILIO_NUMBER = <key>
TWILIO_ACCOUNT_SID = <key>
ASSEMBLYAI_API_KEY = <key>
LANGCHAIN_TRACING_V2 = true
LANGCHAIN_API_KEY =<key>
TAVILY_API_KEY= <key>
ANTHROPIC_API_KEY = <key>
```

# Run script
```
python runner.py
```
