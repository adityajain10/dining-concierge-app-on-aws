import boto3
import json
import random
from boto3.dynamodb.conditions import Key
from botocore.vendored import requests

API_KEY = 'm68Jb9xYu4eUQH0RKbjlFGOj6lzCEEdExprjLAj3Bw8inSDYbODwF1EO13wr1QXaz68XUeoB-Ay-yxwaC4y1KqqHOWc6towlxTvyAXKooWHtYAepY4okWAbeP1SlXHYx'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 1


def lambda_handler(event, context):
    pollSNS()
    # print('\n',yelpResult)
    # insertIntoDynamo()


def pollSNS():
    # create a boto3 client
    client = boto3.client('sqs')
    sms_client = boto3.client('sns')
    # create the test queue
    # for a FIFO queue, the name must end in .fifo, and you must pass FifoQueue = True
    # client.create_queue(QueueName='dinningQueue')
    # get a list of queues, we get back a dict with 'QueueUrls' as a key with a list of queue URLs
    queues = client.list_queues(QueueNamePrefix='restraunt_request')  # we filter to narrow down the list
    test_queue_url = queues['QueueUrls'][0]

    while True:
        # response = client.receive_message(QueueUrl=test_queue_url,AttributeNames=['ALL'],MaxNumberOfMessages=5) # adjust MaxNumberOfMessages if needed
        # Receive message from SQS queue
        response = client.receive_message(
            QueueUrl=test_queue_url,
            AttributeNames=[
                'All'
            ],
            MaxNumberOfMessages=10,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=30,
            WaitTimeSeconds=0
        )

        if 'Messages' in response:  # when the queue is exhausted, the response dict contains no 'Messages' key
            for message in response['Messages']:  # 'Messages' is a list
                js = json.loads(message['Body'])
                # print(json.dumps(js,indent=4,sort_keys=True))
                cuisine = js['cuisine']
                email = js['email']
                phone = js['phone']
                url = 'https://search-restaurant-domain-4hjdrkchdqq3by3xorhorx3dlu.us-east-1.es.amazonaws.com/restaurants/restaurant/_search?from=0&&size=1&&q=Cuisine:' + cuisine
                resp = requests.get(url, headers={"Content-Type": "application/json"}).json()
                n_vals = resp['hits']["total"]
                idx = random.randint(0, n_vals - 1)
                # print(idx)
                url2 = 'https://search-restaurant-domain-4hjdrkchdqq3by3xorhorx3dlu.us-east-1.es.amazonaws.com/restaurants/restaurant/_search?from=' + str(
                    idx) + '&&size=1&&q=Cuisine:' + cuisine
                resp = requests.get(url2, headers={"Content-Type": "application/json"}).json()
                # print(resp)
                res = resp['hits']['hits'][0]['_source']['RestaurantID']
                dbRes = table.query(KeyConditionExpression=Key('insertedAtTimestamp').eq(res))
                print(dbRes)
                # print(type(dbRes['Items'][0]))
                print("-------------------------------")
                # print(dbRes['Items'][0]['name'])
                client.delete_message(QueueUrl=test_queue_url, ReceiptHandle=message['ReceiptHandle'])
                if 'price' in dbRes['Items'][0].keys():
                    price = str(dbRes['Items'][0]['price'])
                else:
                    price = 'NA'
                if 'phone' in dbRes['Items'][0].keys():
                    restaurant_phone = str(dbRes['Items'][0]['phone'])
                else:
                    restaurant_phone = 'NA'
                addr = str(dbRes['Items'][0]['address'])
                for char in "'u[]":
                    addr = addr.replace(char, '')
                message = 'This is an ideal(random) deal for you:\n' + 'Restaurant Name: ' + dbRes['Items'][0][
                    'name'] + '\n' + 'Price: ' + price + '\n' + 'Phone: ' + restaurant_phone + '\n' + 'Address: ' + addr
                check = sms_client.publish(PhoneNumber=str(phone), Message=message)
                # print(str(check))

        else:
            print('Queue is now empty')
            break
