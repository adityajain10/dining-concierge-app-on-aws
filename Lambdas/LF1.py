import json
import os
import math
import dateutil.parser
import datetime
import time
import logging
import boto3
from botocore.vendored import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    
    return response
    
def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


""" --- Functions that control the bot's behavior --- """

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

    
def lambda_handler(event, context):
    # TODO implement
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)
    
def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'GreetingIntent':
        return greeting_intent(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return dining_suggestion_intent(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you_intent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')
    
def greeting_intent(intent_request):
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText', 
                'content': 'Hi there, how can I help?'}
        }
    }

def thank_you_intent(intent_request):
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText', 
                'content': 'You are welcome!'}
        }
    }
def validate_dining_suggestion(location, cuisine, num_people, date, time):
    
    cuisines = ['italian', 'chinese', 'indian', 'american', 'mexican', 'spanish','greek','latin','Persian']
    if cuisine is not None and cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'Cuisine',
                                       'Cuisine not available. Please try another.')
                                       
    if num_people is not None:
        num_people = int(num_people)
        if num_people > 20 or num_people < 0:
            return build_validation_result(False,
                                      'NumberOfPeople',
                                      'Maximum 20 people allowed. Try again')
    
    
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'Date', 'I did not understand that, what date would you like to book?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'Date', 'You can come tomorrow. What time is suitable?')

    if time is not None:
        if len(time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Time', None)

        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Time', 'Not a valid time')

        if hour < 10 or hour > 16:
            # Outside of business hours
            return build_validation_result(False, 'Time', 'Our business hours are from ten a m. to five p m. Can you specify a time during this range?')

    
    return build_validation_result(True, None, None)

def dining_suggestion_intent(intent_request):
    
    location = get_slots(intent_request)["Location"]
    cuisine = get_slots(intent_request)["Cuisine"]
    num_people = get_slots(intent_request)["NumberOfPeople"]
    date = get_slots(intent_request)["Date"]
    time = get_slots(intent_request)["Time"]
    source = intent_request['invocationSource']
    
    
    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)
        
        validation_result = validate_dining_suggestion(location, cuisine, num_people, date, time)
        
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
                               
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        

        return delegate(output_session_attributes, get_slots(intent_request))
        
    # cuisine = get_slots(intent_request)["Cuisine"]
    email = get_slots(intent_request)["Email"]
    phone = get_slots(intent_request)["Phone"]
    sqs = boto3.resource('sqs')

    queue = sqs.get_queue_by_name(QueueName='restraunt_request')
    msg = {"cuisine" : cuisine,"email":email, "phone":phone}
    response = queue.send_message(MessageBody=json.dumps(msg))    
    # Add Yelp API endpoint to get the data
    # requestData = {
    #                 "term":cuisine+", restaurants",
    #                 "location":location,
    #                 "categories":cuisine,
    #                 "limit":"3",
    #                 "peoplenum": num_people,
    #               "Date": date,
    #                 "Time": time
    #             }
    
    # resultData = restaurantApiCall(requestData)

    return close(intent_request['sessionAttributes'],
             'Fulfilled',
             {'contentType': 'PlainText',
              'content': 'Thank you! You will recieve suggestion shortly'})


def restaurantApiCall(requestData):
    
    url = "https://api.yelp.com/v3/businesses/search"
    
    querystring = requestData
    
    payload = ""
    headers = {
        'Authorization': "Bearer m68Jb9xYu4eUQH0RKbjlFGOj6lzCEEdExprjLAj3Bw8inSDYbODwF1EO13wr1QXaz68XUeoB-Ay-yxwaC4y1KqqHOWc6towlxTvyAXKooWHtYAepY4okWAbeP1SlXHYx",
        'cache-control': "no-cache"
        }
    
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

    message = json.loads(response.text)
    
    if len(message['businesses']) < 0:
        return 'Unable to find restaurants'
    
    textString = "Hello! These are my " + requestData['categories'] + " restaurant suggestions for " + requestData['peoplenum'] +" people, for " + requestData['Date'] + " at " + requestData['Time'] + ". "
    count = 1
    for business in message['businesses']:
        textString = textString + " " + str(count) + "." + business['name'] + ", located at " + business['location']['address1'] + " "
        count += 1
    
    textString = textString + " Enjoy your meal!"
    return textString
