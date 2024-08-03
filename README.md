# Catalyst-Labs - Telephonic Eunice

## Overview 

This repo contains the implementation of Eunice AI that can spoken to through Twilio integration ! 

Eunice AI is an AI customer service agent that is built to enbale small businesses to have the power of information found in a website... telephonically, and the best part is that they do not have to worry about answering calls, Eunice does that ! 

## Technical Overview 

This enitre codebase was configured and deployed using AWS EC2 , running on an m5.large with Amazon Linux 2 . It used: 
- `Nginx`: Acts as a reverse proxy to handle traffic for both the **REST APIs** and **WebSockets** that we built. Traffic is handled through http port 80 (ideally, we would use a self-signed SSL certificate for secure connections).
- `Gunicorn` : We started and enabled a websocket.service systemd file to execute our Flask application as soon as the network target is reached, ensuring it remains running and accessible. The file websocket.service file looks something like this:
```
[Unit]
Description=Gunicorn daemon to run Cataylyst Lab's REST Apis and Webockets 
After=network.target 

[Service]
User=ec2-user
Group=www-data
WorkingDirectory=/home/ec2-user/Catalyst-Labs
ExecStart=/bin/bash -c "source /home/ec2-user/anaconda3/etc/profile.d/conda.sh && conda activate py310  && exec gunicorn --worker-class gevent --bind unix:/home/ec2-user/Catalyst-Labs/websocket.sock --workers 3 --timeout 120 runner:app 
Restart=always
Environment="PATH=/home/ec2-user/anaconda3/envs/py310/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=multi-user.target
```

**NOTE:** Deployment to ec2 is a seperate matter that has a lot of naunces and configurations,if you  would like a guide to deploy this on your own ec2 instance, feel free to reach out ! 

We also used a few `3rd parties`: 
- Twilio: We bought a phone number: `+27 87 250 0467` for customers to be able to call
- AssemblyAI: We built a websocket to stream speech to text using the audio bytes from Twilio
- Groq: Groq was used for fast inference for the LLM Agents that we built
- Pincone: Vector database to store knowledge on the customer
- MongoDb: stores all the data from the conversation on the phone
- NGROK: We used ngrok to tunnel traffic from our server to store it in the Twilio webhookUrl for our phone number, in order for our webhook to establish a connection and parse audio streams for transcription.

## Pre-setup 

1. MongoDb

You will need to have a mongodb url to use to store you applicaiton data. 
- Create the database and collections found in the file: `/api/config/mongodb_config.py`
- Get your MONGO URI, you will need to paste it in the `.env` file.  

2. AWS (only applies if you want to use the APIs, but for this Quick start demo, you will not need to do this) 
- To access the public s3 bucket through boto3, you will need to configure your console with AWS credentials
```
# Run 
aws configure

# You will be prompted to add
SECRET KEY: <key>
ACCESS KEY: <key>
REGION : af-south-1
FORMAT: json 
```

3. Twilio
- Twilio is needed to for the VoIP compoenent. You will need to setup a twilio account and add your:
```
TWILIO_API_KEY_SID =<key>
TWILIO_API_SECRET= <key>
TWILIO_NUMBER = <key>
TWILIO_ACCOUNT_SID = <key>
```
- Twilio does provide you with an international number that you can use to call, but if are not based in USA , the carrier charges will be expensive, so just be prepared for your airtime to ... evaporate. You can purchase a number from Twilio and it will take 24-48 hours for them to verify your documents before granting you a south african number.
- Create your API key under: account management > API keys > create API key
  
**Note** In order for you to call your number, your number must be verified under `verified call id`, so just make sure you are calling from a number that is there

# Setup

## Configure Environment (Conda or Venv)

1. Conda
```
#Create conda environment 

conda create -n <environment name> python=3.10

# Activate conda environment 
conda activate <environment name>

```

## Pip install requirements 

```
pip install -r requirements.txt
```

## Setup ENV variables in `.env`
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


## Contributing

We welcome contributions! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

