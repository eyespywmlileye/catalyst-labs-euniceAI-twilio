
import boto3
from dotenv import load_dotenv
from flask import Blueprint, jsonify

from api.v1.contants.http_status_codes import *

load_dotenv()

aws_object_store = Blueprint('aws_object_store', 
                              __name__, 
                              url_prefix='/api/v1/aws_object_store')


@aws_object_store.route('/get_document/<string:file_name>', methods=['GET'])
def get_documnet_from_s3_bucket(file_name: str):
    
    bucket_name: str = "nerdma-hackathon"
    s3 = boto3.client('s3')
    
    try:
        s3.download_file(bucket_name, file_name, file_name)
        return jsonify({"message": "Document downloaded successfully"}), HTTP_200_OK
    
    except Exception as e:
        return jsonify({"message": f"Document not found: {e}"}), HTTP_404_NOT_FOUND



@aws_object_store.route('/upload_document/<string:file_name>', methods=['POST'])
def upload_document_to_s3_bucket(file_name: str):
    
    bucket_name: str = "nerdma-hackathon"
    s3 = boto3.client('s3')
    try: 
        s3.upload_file(file_name, bucket_name, file_name)
        return jsonify({"message": "Document uploaded successfully"}), HTTP_200_OK
    
    except Exception as e:
        return jsonify({"message": f"Document not uploaded: {e}"}), HTTP_400_BAD_REQUEST