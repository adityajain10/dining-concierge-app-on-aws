import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')
fn = getattr(requests, 'post')


def send(url, body=None):
    fn(url, data=body,
       headers={"Content-Type": "application/json"})

def putRequests():
    resp = table.scan()
    i = 1
    url = 'https://search-restaurant-domain-4hjdrkchdqq3by3xorhorx3dlu.us-east-1.es.amazonaws.com/restaurants/restaurant'
    headers = {"Content-Type": "application/json"}
    while True:
        #print(len(resp['Items']))
        for item in resp['Items']:
            body = {"RestaurantID": item['insertedAtTimestamp'], "Cuisine": item['cuisine']}
            r = requests.post(url, data=json.dumps(body).encode("utf-8"), headers=headers)
            #print(r)
            i += 1
            #break;
        if 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ExclusiveStartKey=resp['LastEvaluatedKey']
            )
            #break;
        else:
            break;
    print(i)
