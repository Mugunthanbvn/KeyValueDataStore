import requests
import json
from sys import getsizeof
import subprocess
try :
    import RequestHandler
    #RequestHandler.start_server()
    subprocess.Popen("python RequestHandler.py")
except Exception:
    print("Server(RequestHandler.py) Should Be start Manually")
#from RequestHandler import Server

class Response:
    
    def __init__(self,response):
        self.json = response
        self.value = response.get("value")
        self.message = response.get("message")
        self.is_success = bool(response.get("success"))
        self.access_config = response.get("access_config")
class DataStore:
    
    def __init__(self,path= "",url=None):
        if(url==None):
            self.url = "http://localhost:80"
        else:
            self.url = url
        self.filepath = path
        self.auth_token = ""
        self.access_config ={"auth_token":self.auth_token,"filepath":self.filepath}
       
        pass
    def validate_key(self,key):
      if(len(key)>32):
          print("Key length must be caped to 32 characters")
          return False
      return True
    def validate_value(self,value):
       value_size = len(str(value)) 
       if(value_size/10000 > 16):   
            print("Value must be caped to 16KB")
            return False
       return True  
    def create(self,key,value,time_to_live=-1):
        response_obj = None
        try:
            print(self.access_config)
            requestpath= "/datastore/create"
            valid=self.validate_key(key)
            value_json = json.dumps(value)
            valid = valid and self.validate_value(value)    
            if(valid):
                response = requests.post(self.url+requestpath,data={"access_config":json.dumps(self.access_config),key:value_json,"time_to_live":time_to_live})
                response_obj = Response(json.loads(response.text))
                self.access_config = response_obj.access_config
                print(self.access_config)
        except Exception as error:
            print(error)
        
        return response_obj
    def view(self,key):
        response_obj = None
        try:
            requestpath= "/datastore/view"
            valid = self.validate_key(key)
            if(valid):
                response = requests.post(self.url+requestpath,data={"access_config":json.dumps(self.access_config),key:""})
            
                response_obj = Response(json.loads(response.text))
                self.access_config = response_obj.access_config
        except Exception as error:
            print(error)
        return response_obj
    def delete(self,key):
        response_obj = None
        try:
            requestpath= "/datastore/delete"
            
            valid = self.validate_key(key)
            if(valid):
                response = requests.post(self.url+requestpath,data={"access_config":json.dumps(self.access_config),key:""})
            
                response_obj = Response(json.loads(response.text))
                self.access_config = response_obj.access_config
        except Exception as error:
            print(error)
        return response_obj

    def close(self):
        try:
            requestpath= "/datastore/release"
            response = requests.post(self.url+requestpath,data={"access_config":json.dumps(self.access_config)})
            response_obj = Response(json.loads(response.text))
            return response_obj
        except Exception as error:
            print(error)     




'''
Examples :
data_store = DataStore()
response = data_store.create("key",{"hi":{"hi":"1"},"hi2":{"hi":"2"}})
print(response.message)

response=data_store.view("key")
print(response.value)

response=data_store.delete("key")
print(response.message)

response=data_store.close()
print(response.message)

'''