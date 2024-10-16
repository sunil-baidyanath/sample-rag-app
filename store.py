'''
Created on Oct 15, 2024

@author: sunilthakur
'''
import os
import shutil

from azure.storage.blob import BlobServiceClient, BlobClient


class BlobStorageStore(object):
    
    def __init__(self, container, access_key):
        service_client = BlobServiceClient(account_url="https://arogyares.blob.core.windows.net", 
                                                                  credential=access_key)
        self.container_name = container
        self.access_key = access_key
        self.container_client = service_client.get_container_client(container)
    
    def exists_file(self, file_name):
        print("Checking for file: ", file_name)
        
        blob = BlobClient(account_url="https://arogyares.blob.core.windows.net",
                          container_name=self.container_name,
                          blob_name=file_name,
                          credential=self.access_key)
        
        return blob.exists()
        
    def download_file(self, file_name, path=None):
        print(file_name)
        blob = BlobClient(account_url="https://arogyares.blob.core.windows.net",
                          container_name="documents",
                          blob_name=file_name,
                          credential=self.access_key)
            
        target_filename = os.path.join(path, os.path.basename(file_name))
        with open(file=target_filename, mode="wb") as f:
            data = blob.download_blob()
            data.readinto(f)
            
    def download_files(self, blobs_path):
        if os.path.exists(blobs_path):
            shutil.rmtree(blobs_path)    
        os.makedirs(blobs_path)
                
        for blob in self.container_client.list_blobs(name_starts_with=blobs_path):  
            blob_client = self.container_client.get_blob_client(blob)
            target_filename = os.path.join(blobs_path, os.path.relpath(blob.name, blobs_path))
            
            with open(file=target_filename, mode="wb") as f:
                data = blob_client.download_blob()
                data.readinto(f)
            
            
    def upload_file(self, file_path, folder_path=None):
        blob = BlobClient(account_url="https://arogyares.blob.core.windows.net",
                          container_name="indexes",
                          blob_name=os.path.relpath(file_path, folder_path), 
                          credential=self.access_key)
        
        # print(os.path.relpath(file_path, folder_path))
        with open(file_path, "rb") as data:
            blob.upload_blob(data)
        
        
    def upload_folder(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # print(file_path)
                self.upload_file(file_path, os.path.dirname(folder_path))
        
