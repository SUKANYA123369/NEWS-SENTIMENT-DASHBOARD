import os
import json
import requests
import boto3
import psycopg2
from datetime import datetime

NEWS_API_KEY = os.environ['NEWS_API_KEY']
S3_BUCKET = os.environ['S3_BUCKET']
S3_PREFIX = os.environ.get('S3_PREFIX', 'rawdata_2/') 
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_NAME = os.environ['DB_NAME']
TABLE_NAME = 'import os
import json
import requests
import boto3
import psycopg2
from datetime import datetime

NEWS_API_KEY = os.environ['NEWS_API_KEY']
S3_BUCKET = os.environ['S3_BUCKET']
S3_PREFIX = os.environ.get('S3_PREFIX', 'rawdata_2/') 
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_NAME = os.environ['DB_NAME']
TABLE_NAME = 'news_dashhboard'

s3 = boto3.client('s3')

def get_news():
    url = f'https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch news: {response.status_code} {response.text}")

def upload_to_s3(data):
    s3_file_key = f'{S3_PREFIX}news_{datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")}.json'
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_file_key,
        Body=json.dumps(data),
        ContentType='application/json'
    )
    print(f"File uploaded to s3://{S3_BUCKET}/{s3_file_key}")

def ensure_table_exists(conn):
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        source_id VARCHAR(100),
        source_name VARCHAR(255),
        author TEXT,
        title TEXT,
        description TEXT,
        url TEXT,
        url_to_image TEXT,
        published_at TIMESTAMP,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        
        
    );
    '''
    with conn.cursor() as cur:
        cur.execute(create_table_query)
        conn.commit()
    print(f"Table '{TABLE_NAME}' created or already exists.")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        dbname=DB_NAME
    )

def load_data_from_s3_to_rds(conn):
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)

    if 'Contents' not in response:
        print("No files found in S3 folder.")
        return

    insert_query = f'''
        INSERT INTO {TABLE_NAME} (
            source_id, source_name, author, title, description, url,
            url_to_image, published_at, content
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''

    with conn.cursor() as cur:
        for obj in response['Contents']:
            key = obj['Key']

            if key.endswith('/'): 
                continue

            file_obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
            file_content = file_obj['Body'].read()

            if not file_content:
                print(f"Skipping empty file: {key}")
                continue

            try:
                data = json.loads(file_content)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON file {key}: {e}")
                continue

            articles = data.get('articles', [])
            for article in articles:
                source = article.get('source', {})
                source_id = source.get('id')
                source_name = source.get('name')
                author = article.get('author')
                title = article.get('title')
                description = article.get('description')
                url = article.get('url')
                url_to_image = article.get('urlToImage')
                published_at = article.get('publishedAt')
                content = article.get('content')

                if published_at:
                    
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                else:
                    published_at = None

                cur.execute(insert_query, (
                    source_id, source_name, author, title, description, url,
                    url_to_image, published_at, content
                ))

        conn.commit()
    print("Data loaded from S3 to RDS successfully.")

def lambda_handler(event, context):
    try:
    
        news_data = get_news()
        upload_to_s3(news_data)

        
        conn = get_db_connection()
        ensure_table_exists(conn)

        
        load_data_from_s3_to_rds(conn)

        conn.close()

        return {
            "statusCode": 200,
            "body": "News fetched, uploaded to S3, and loaded into RDS successfully."
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {
            "statusCode": 500,
            "body": f"Error occurred: {str(e)}"
        }'

s3 = boto3.client('s3')

def get_news():
    url = f'https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch news: {response.status_code} {response.text}")

def upload_to_s3(data):
    s3_file_key = f'{S3_PREFIX}news_{datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")}.json'
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_file_key,
        Body=json.dumps(data),
        ContentType='application/json'
    )
    print(f"File uploaded to s3://{S3_BUCKET}/{s3_file_key}")

def ensure_table_exists(conn):
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        source_id VARCHAR(100),
        source_name VARCHAR(255),
        author TEXT,
        title TEXT,
        description TEXT,
        url TEXT,
        url_to_image TEXT,
        published_at TIMESTAMP,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        
        
    );
    '''
    with conn.cursor() as cur:
        cur.execute(create_table_query)
        conn.commit()
    print(f"Table '{TABLE_NAME}' created or already exists.")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        dbname=DB_NAME
    )

def load_data_from_s3_to_rds(conn):
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)

    if 'Contents' not in response:
        print("No files found in S3 folder.")
        return

    insert_query = f'''
        INSERT INTO {TABLE_NAME} (
            source_id, source_name, author, title, description, url,
            url_to_image, published_at, content
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''

    with conn.cursor() as cur:
        for obj in response['Contents']:
            key = obj['Key']

            if key.endswith('/'): 
                continue

            file_obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
            file_content = file_obj['Body'].read()

            if not file_content:
                print(f"Skipping empty file: {key}")
                continue

            try:
                data = json.loads(file_content)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON file {key}: {e}")
                continue

            articles = data.get('articles', [])
            for article in articles:
                source = article.get('source', {})
                source_id = source.get('id')
                source_name = source.get('name')
                author = article.get('author')
                title = article.get('title')
                description = article.get('description')
                url = article.get('url')
                url_to_image = article.get('urlToImage')
                published_at = article.get('publishedAt')
                content = article.get('content')

                if published_at:
                    
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                else:
                    published_at = None

                cur.execute(insert_query, (
                    source_id, source_name, author, title, description, url,
                    url_to_image, published_at, content
                ))

        conn.commit()
    print("Data loaded from S3 to RDS successfully.")

def lambda_handler(event, context):
    try:
    
        news_data = get_news()
        upload_to_s3(news_data)

        
        conn = get_db_connection()
        ensure_table_exists(conn)

        
        load_data_from_s3_to_rds(conn)

        conn.close()

        return {
            "statusCode": 200,
            "body": "News fetched, uploaded to S3, and loaded into RDS successfully."
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {
            "statusCode": 500,
            "body": f"Error occurred: {str(e)}"
        }
