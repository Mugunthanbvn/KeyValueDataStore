from flask import Flask,request
import os
import json
from sys import getsizeof
import time
import secrets
import argparse

SERVER_CONFIG = {
    "url" : "localhost",
    "port" : 80,
    "base_path" : os.path.join(os.getcwd(),"DataStore"),
    "max_file_size" : 10**9 , #IN BYTES
    "file_name" : "DataStore.json",
    
    }

app = Flask(__name__)
files_in_access ={}
class JsonParser :
    
    def __init__(self,filepath,max_file_size):
       self.filepath = filepath 
       self.max_file_size =max_file_size
       if(not os.path.exists(self.filepath)  ):
           self.create_file()
       self.FILE_CONFIG = self.read_file_config()
    
    def read_file_config (self):
        with open(self.filepath,"r") as data_file:
            data_file.readline()
            self.FILE_CONFIG = json.loads("{%s}"%data_file.readline())["FILE_CONFIG"]
            return self.FILE_CONFIG
    
    def put_file_config(self,config):
        with open(self.filepath,"rb+") as data_file:
            data_file.readline()
            config='''"FILE_CONFIG":%s'''%(json.dumps(config))

            data_file.write(bytes(config,encoding="utf-8"))

    def create_file(self):
        with open(self.filepath,"w+") as data_file:
            FILE_CONFIG = '''{\n"FILE_CONFIG":{"Start": "%s" ,"End": "%s"}\n}'''%(format(-1,"08x"),format(-1,"08x"))
            data_file.write(FILE_CONFIG)
    
    def get_config(self,key_pointer):
        key_loc= key_pointer.tell()
        key=key_pointer.readline().decode()
 
        key = key[1:-4]
        config=json.loads("{%s}"%key_pointer.readline().decode())["CONFIG"]
        key_pointer.seek(key_loc)
 
        return key,config
   
    def put_config(self,key_pointer,config):
        key_loc= key_pointer.tell()
        key=key_pointer.readline().decode()
        config='''"CONFIG":%s'''%(json.dumps(config))
        key_pointer.write(bytes(config,encoding="utf-8"))
        key_pointer.seek(key_loc)
        return 
    def go(self,key_pointer,move):
        if(move=="next"):
            key,config=self.get_config(key_pointer)
            next_node = int(config["Next"],16)
            key_pointer.seek(next_node)
        elif(move=="previous"):
            key,config=self.get_config(key_pointer)
            previous_node = int(config["Previous"],16)
            key_pointer.seek(previous_node)

    def get_data(self,key_pointer):
        key_loc= key_pointer.tell()
        key=key_pointer.readline().decode()
        key = key[1:-4]
        config=json.loads("{%s}"%key_pointer.readline().decode())["CONFIG"]
        #value_end = value_start + config["Size"]
        value=key_pointer.read(int(config["Size"])).decode()[1:].strip()
        value2="{%s"%(value)

        value=json.loads(value2)["VALUE"]
        key_pointer.seek(key_loc)
        return key,config,value

    def is_exists(self,key):
        with open(self.filepath,"rb") as data_file:
            start,end=self.FILE_CONFIG["Start"],self.FILE_CONFIG["End"]
            start,end=int(start,base=16),int(end,base=16)
            node = start
            if(start!=-1):
                data_file.seek(node)
                node_key,node_config = self.get_config(data_file)
          
                while(node_key!=key and node!=end):
          
                    self.go(data_file,"next")
                    node=data_file.tell()
          
                    node_key,node_config = self.get_config(data_file)
          
                if(node_key==key):
                    return node
        return None
    def create(self,key,value,time_to_live=None):
        status = {}
        if(os.stat(self.filepath).st_size<=self.max_file_size):
            key_loc=self.is_exists(key)
            
            
            if(key_loc==None):
                with open(self.filepath,"rb+") as data_file:
                    previous_node , next_node =None ,None
                    last = data_file.seek(0,2)
                    last_node = int(self.FILE_CONFIG["End"],16)
                    previous_node = last_node
                    next_node = None
                    if(last_node !=-1):
                        data_file.seek(last_node)
                        #Update next
                        
                        node_key,node_config = self.get_config(data_file)
                        node_config["Next"] = format(last,"08x")
                        self.put_config(data_file,node_config)

                    else:
                        previous_node = None

                    #Update Previous
                    
                    data_file.seek(-1,2)
                    previous_node = format(-1,"08x") if (previous_node==None) else format(previous_node,"08x")
                    next_node = format(-1,"08x") if (next_node==None) else format(next_node,"08x")
                    time_to_live  = format(-1,"010") if(time_to_live==-1) else int(time_to_live)+int(time.time())
                    config = '''{"Previous": "%s", "Next": "%s", "time_to_live": "%s", "Size": "%d"}'''%(previous_node,next_node,time_to_live,len(value)+12)
                    data = ''',"%s":{\n"CONFIG":%s\n,\n"VALUE":%s\n}\n}'''%(key,config,value)

                    key_loc=data_file.tell()+1
                    
                    
                    data_file.write(bytes(data,encoding="utf-8"))
                    if(int(self.FILE_CONFIG["Start"],16)==-1):
                        self.FILE_CONFIG["Start"] = format(key_loc,"08x")
                    
                    self.FILE_CONFIG["End"] = format(key_loc,"08x")
                    self.put_file_config(self.FILE_CONFIG)
                    status["success"] = True
                    status["message"] = "Key Created Successfully"
                    return status
            status["success"] = False
            status["message"] = "Key Already Exists"    
        
        
        else:
            status["success"] = False
            status["message"] = "File Size Exceeded" 
        
        return status

    def delete(self,key):
        key_loc=self.is_exists(key)
        status = {}
        if(key_loc!=None):
            #correct error
            with open(self.filepath,"rb+") as data_file:
                data_file.seek(key_loc)
                node_key,node_config=self.get_config(data_file)
                flg=True
                if(key_loc==int(self.FILE_CONFIG["Start"],16) ) :
                    self.FILE_CONFIG["Start"] = node_config["Next"]
                    flg=False     
                if(key_loc==int(self.FILE_CONFIG["End"],16)):
                    self.FILE_CONFIG["End"] = node_config["Previous"]
                    
                
                if(flg):
                    previous=node_config["Previous"] 
                    data_file.seek(int(previous,16))
                    pre_key,pre_config=self.get_config(data_file)
                    pre_config["Next"] = node_config["Next"]
                    self.put_config(data_file,pre_config)
                
                self.put_file_config(self.FILE_CONFIG)
                status["success"] = True
                status["message"] = "Deleted Successfully"
                return status
                
        status["success"] = False
        status["message"] = "Key Not Found"    
        return status

    def view(self,key):
        key_loc=self.is_exists(key)
        status = {}
        if(key_loc!=None):
            with open(self.filepath,"rb+") as data_file:
                data_file.seek(key_loc)
                key,config,value=self.get_data(data_file)
                

                
                time_to_live = int(config["time_to_live"])
                if(time_to_live!=-1):
                    if(time_to_live<time.time()):
                        status["success"] = False
                        status["message"] = "Time Limit Exceded" 
                        status["value"] = None
                    else:
                        status["success"] = True
                        status["message"] = "Data Retrived"    
                        status["value"] = value
                else:
                    status["success"] = True
                    status["message"] = "Data Retrived"    
                    status["value"] = value

                return status
        status["success"] = False
        status["message"] = "Key Not Found"    
        return status

def get_file_parser(access_config):
    auth_token,filepath=access_config["auth_token"],access_config["filepath"]
    js_parser = None
    status = {}
    if(files_in_access.get(filepath)!=None):
        file_auth,file_parser = files_in_access.get(filepath)
        
        if(auth_token == file_auth):
            js_parser = file_parser
        else :
            
            status["message"] = "File already in Use"
            status["success"] = False
            status["access_config"] = access_config 

    else:
        access_config["auth_token"] = secrets.token_hex(4)
        #create new file if not exists
        if(filepath==""):
            filepath = os.path.join(SERVER_CONFIG["base_path"],SERVER_CONFIG["file_name"])
            if(os.path.exists(filepath)):
                filepath  =os.path.join(SERVER_CONFIG["base_path"],SERVER_CONFIG["file_name"]+"_"+str(int(time.time())))  
        access_config["filepath"] = filepath
        js_parser = JsonParser(filepath,SERVER_CONFIG["max_file_size"])
        files_in_access[filepath] = [access_config["auth_token"],js_parser]
    
        
    return js_parser,status,access_config

@app.route("/datastore/create",methods=["POST"])
def create():

    form=dict(request.form)
    form_items = list(form.items())
    access_configstr,access_config = form_items[0]
    
    access_config = json.loads(access_config)
    
    js_parser ,status,access_config = get_file_parser(access_config)
    if(js_parser==None):
        return json.dumps(status)
    
    key,value = form_items[1]
    timestr,time_to_live = form_items[2]
    status = js_parser.create(key,value,int(time_to_live))
    status["access_config"] = access_config
    return json.dumps(status)

@app.route("/datastore/delete",methods=["POST"])
def delete():
    form=dict(request.form)
    form_items = list(form.items())
    
    access_configstr,access_config = form_items[0]
    access_config = json.loads(access_config)
    
    js_parser ,status,access_config = get_file_parser(access_config)
    if(js_parser==None):
        return json.dumps(status)
    
    key,value = form_items[1]

    status = js_parser.delete(key)
    status["access_config"] = access_config
    return json.dumps(status)
@app.route("/datastore/view",methods=["POST"])
def view():
    form=dict(request.form)
    form_items = list(form.items())
    access_configstr,access_config = form_items[0]
    access_config = json.loads(access_config)
    
    js_parser ,status,access_config = get_file_parser(access_config)
    if(js_parser==None):
        return json.dumps(status)
    
    key,value = form_items[1]
    status = js_parser.view(key)
    status["access_config"] = access_config
    return json.dumps(status)


@app.route("/datastore/release",methods=["POST"])
def release():
    form=dict(request.form)
    form_items = list(form.items())
    status ={}
    access_configstr,access_config = form_items[0]
    access_config = json.loads(access_config)
    if(access_config["filepath"] in files_in_access):
        file_auth,file_parser = files_in_access.get(access_config["filepath"])
        if(access_config.get("auth_token")==file_auth):
            status["message"] = "File resource released Successfully "
            status["success"] = True
            status["access_config"] = access_config
            files_in_access.pop(access_config["filepath"])
            return json.dumps(status)

    status["message"] = "File used by some other clients"
    status["success"] = False
    status["access_config"] = access_config

    return json.dumps(status)

basepath,filename = SERVER_CONFIG["base_path"],SERVER_CONFIG["file_name"]
filepath = os.path.join(basepath,filename)  
js_parser = None


def start_server(CONFIG=SERVER_CONFIG,filepatharg=None):
    global js_parser,app
    
    basepath,filename = CONFIG["base_path"],CONFIG["file_name"]
    if(not os.path.exists(basepath)):
        os.mkdir(basepath)
    
    filepath = os.path.join(basepath,filename)  
    if(filepatharg!=None):

        filepath=filepatharg

    js_parser = JsonParser(filepath,CONFIG["max_file_size"])                    
    
    app.run("localhost",str(CONFIG["port"]),debug=True)

#same file name in one dir

if(__name__=="__main__"):
    try:
        description ='''
        Server For Handling Request to perform CRD operations on Key-Value[JSON]
        DataServer.
        Enjoy!,Storing Data :)
        ''' 
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("-u","--url",help ="url to start server, Eg : -u http://localhost,")
        parser.add_argument("-p","--port",help ="port to start server, Eg: -p 80,")
        parser.add_argument("-b","--base_path",help ="path of working directory, Eg: -b E:/MyDataStore")
        parser.add_argument("-f","--file_name",help ="Name of Data file , Eg: -f Datafile.json")
        parser.add_argument("-m","--max_file_size",help ="Max Size Of File In Bytes, Eg -m 100000000")
        args = parser.parse_args()
        for arg,value in args._get_kwargs():
            if(value!=None):
                SERVER_CONFIG[arg] = value
        
        start_server(SERVER_CONFIG)
    except Exception as error:
        print(error)


