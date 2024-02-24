from pymongo import MongoClient
import os, boto3

client = MongoClient(os.environ.get('MONGO_URI'))
db = client['blogs']
blogs_table = db['new_blogs_table']
keywords_table = db['keywords_table']
cred_table = db['cred_table']
user_table = db['user_table']

s3 = boto3.resource(
    's3',
    region_name=os.environ.get('AWS_REGION'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)