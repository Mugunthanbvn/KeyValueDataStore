File - DataStore :


PROBLEM STATEMENT :

The data store will support the following functional requirements.

 1.It can be initialized using an optional file path. If one is not provided, it will reliably create itself in a reasonable location on the laptop.
 
 2.A new key-value pair can be added to the data store using the Create operation. The key is always a string - capped at 32chars. The value is always a JSON object - capped at 16KB.
   If Create is invoked for an existing key, an appropriate error must be returned.

 3.A Read operation on a key can be performed by providing the key, and receiving the value in response, as a JSON object.
 
 4.A Delete operation can be performed by providing the key.
 
 5.Every key supports setting a Time-To-Live property when it is created. This property is optional. If provided, it will be evaluated as an integer defining the number of seconds the key must be retained in the data store. Once the Time-To-Live for a key has expired, the key will no longer be available for Read or Delete operations.

 6.Appropriate error responses must always be returned to a client if it uses the data store in unexpected ways or breaches any limits.

The data store will also support the following non-functional requirements.

 1.The size of the file storing data must never exceed 1GB.

 2.More than one client process cannot be allowed to use the same file as a data store at any given time.

 3.A client process is allowed to access the data store using multiple threads, if it desires to. The data store must therefore be thread-safe.
 
 4.The client will bear as little memory costs as possible to use this data store, while deriving maximum performance with respect to response times for accessing the data store.

IDEA :
Unaltering the file format(JSON) , A Parser like code has been implemented which optimises the CRD operations
by concept of storing address on linked list like structure and accessing using file seek operation.

PROCEDURE :
 
1.Configure url,port and other configurations on RequestHandler.py

2.Start the server by running the RequestHandler.py file on Server

3.To send requests to the server, Inistialize the class file in Datastore.py and use appropriate CRD functions to pass requests to the sever with required parameters.

4.The Key-Value data is stored in .json file on given path or file will created by server itself and filepath will be retuened and stored on access_config in response

5.Appropriate responses will be send from the FLASK  functions
