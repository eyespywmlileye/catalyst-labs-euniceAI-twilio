import os
import boto3
from dotenv import load_dotenv
from flask import Blueprint, jsonify

from api.contants.http_status_codes import *

load_dotenv()


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME: str = "nerdma-ai-receptionist"


aws_object_store = Blueprint('aws_object_store', 
                              __name__, 
                              url_prefix='/api/v1/aws_object_store')


@aws_object_store.route('/get_document/<string:file_name>', methods=['GET'])
def get_documnet_from_s3_bucket(file_name: str):

    s3 = boto3.client(
        's3',
        aws_access_key_id= AWS_ACCESS_KEY_ID,
        aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
        region_name='af-south-1'
        )
    
    try:
        s3.download_file(BUCKET_NAME, file_name, file_name)
        return jsonify({"message": "Document downloaded successfully"}), HTTP_200_OK
    
    except Exception as e:
        return jsonify({"message": f"Document not found: {e}"}), HTTP_404_NOT_FOUND



@aws_object_store.route('/upload_document/<string:file_name>', methods=['POST'])
def upload_document_to_s3_bucket(file_name: str):
    
    s3 = boto3.client(
        's3',
        aws_access_key_id= AWS_ACCESS_KEY_ID,
        aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
        region_name='af-south-1'
        )
    try: 
        s3.upload_file(file_name, BUCKET_NAME, file_name)
        return jsonify({"message": "Document uploaded successfully"}), HTTP_200_OK
    
    except Exception as e:
        return jsonify({"message": f"Document not uploaded: {e}"}), HTTP_400_BAD_REQUEST