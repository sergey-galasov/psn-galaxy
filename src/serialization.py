import base64
import pickle

def loads(s):
    return pickle.loads(base64.decodebytes(s.encode()))

def dumps(obj):
    return base64.encodebytes(pickle.dumps(obj)).decode()
