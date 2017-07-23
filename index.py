# -*- coding: utf-8 -*-

data_dir = "/tmp/"
import json
import os
import base64
import random
import traceback
from grabber import grabber
def grab(username=None, password=None, err=None):
    try:
        if err:
            raise Exception(err)
        if not all((username,password)):
            raise Exception("username and password both required")
        temp_filename = data_dir+'%s_%.8x.ics' %(username,random.getrandbits(32))
        err = grabber(username,password,temp_filename)
        if not os.path.exists(temp_filename):
            raise Exception(err)
    except Exception as err:
        #traceback.print_exc()
        return {
            "isBase64Encoded": True,
            "statusCode": 500,
            "headers":{
                "Content-Type": "text/html; charset=utf-8",
            },
            "body": base64.b64encode("Error: %s <br><a href='javascript:window.history.go(-1)'>戳我返回</a>"%err),
        }
    return {
            "isBase64Encoded": True,
            "statusCode": 200,
            "headers":{
                "Content-Type": "application/octet-stream",
                "Content-Disposition": 'attachment; filename="%s.ics"'%username
            },
            "body": base64.b64encode(open(temp_filename,'rb').read()),
        }

def index(event, context):
    try:
        event = json.loads(event)
        body = json.loads(event["body"])
        return grab(body["username"],body["password"])
    except Exception as e:
        return grab(err="Invalid input %s %s"%(e,event))

if __name__ == '__main__':
    import sys
    from pprint import pprint
    pprint(grab(sys.argv[1],sys.argv[2]))