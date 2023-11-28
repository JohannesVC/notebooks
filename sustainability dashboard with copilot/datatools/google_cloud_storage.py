from google.cloud import storage
import io
import datetime
from utils.jwt_config import user_id_in_token, username_in_token, fund_link_in_token
import os
from urllib.parse import urlparse, unquote
import logging
from api_orion import env
import json
from google.oauth2.service_account import Credentials

class GoogleCloudStorage:
    def __init__(self):
        sa_info = json.loads(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON"))
        credentials = Credentials.from_service_account_info(sa_info)
        
        self.storage_client = storage.Client(credentials=credentials)
        
        # if env == 'production':
            
        #     logging.info("Initialising google's storage.Client()")
        # else:
        #     self.storage_client = storage.Client.from_service_account_json('google_credentials.json')
        #     logging.info("Initialising google's storage.Client.from_service_account_json('google_credentials.json')")
        
    def init_visualiser(self):
        self.bucket = self.storage_client.bucket("visualiser")
        self.user_id = user_id_in_token()
        self.user_name = username_in_token()
        self.fund_id = fund_link_in_token()
    
    def save_png(self, ax):
        self.init_visualiser()        
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y%m%dT%H%M%S")
        filename = f"image_{formatted_date}.png"
        blob_name = f'temp/{self.fund_id}/{self.user_name}/{filename}'
        blob = self.bucket.blob(blob_name)
        
        buffer = io.BytesIO()
        ax.figure.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        blob.upload_from_file(buffer, content_type='image/png')
        self.generate_signed_url(blob_name)
        return blob_name

    def generate_signed_url(self, blob_name):
        blob = self.bucket.blob(blob_name)
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(days=7),
            method="GET")
        return url
    
    def add_url_to_overview(self, url):
        self.init_visualiser()   
        print(url)
        parsed_url = urlparse(url)
        path = parsed_url.path.split('/')
        assert 'temp' in path[2], "temp is not in path"
        fund_id = path[3]
        user_name = unquote(path[4])
        filename = unquote(path[5]) 

        source_blob_name = f'temp/{fund_id}/{user_name}/{filename}'
        destination_blob_name = f'{fund_id}/{user_name}/{filename}'

        source_blob = self.bucket.blob(source_blob_name)
        
        if not source_blob.exists():
            print(f"Blob {source_blob_name} does not exist. Maybe it is added already?")
            return

        new_blob = self.bucket.copy_blob(source_blob, self.bucket, destination_blob_name)
        source_blob.delete()
        logging.info("Moved image file to: ", str(new_blob))
        
    def get_selected(self):
        self.init_visualiser()   
        prefix = f"{self.fund_id}/{self.user_name}"
        blobs = self.bucket.list_blobs(prefix=prefix)
        most_recent_blobs = sorted(blobs, key=lambda x: x.name, reverse=True)[:9]
        
        image_urls = {}
        slots = ['topleft', 'topmiddle', 'topright', 
                'middleleft', 'middlemiddle', 'middleright',
                'bottomleft', 'bottommiddle', 'bottomright']

        for slot, most_recent_file in zip(slots, most_recent_blobs):
            signed_url = self.generate_signed_url(most_recent_file.name)

            image_urls[slot] = signed_url
        return image_urls