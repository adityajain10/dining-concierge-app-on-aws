import json
import boto3


client = boto3.client('lex-runtime')

def lambda_handler(event, context):
    
    lastUserMessage = event['message'];
    botMessage = "Please try again.";
    #cognito = boto3.client('cognito-idp')
    print type(event);
    user = event['identityID']
    #access_token = str(event["id_token"]);
    #resp = cognito.get_user(
    #AccessToken=access_token
    #)
    #print("The cog "+access_token)
   
    
    # userattr = resp['UserAttributes']
    # email = ''
    # for val in userattr:
    #     if val['Name'] == 'email':
    #         email = val['Value']
   
    if lastUserMessage is None or len(lastUserMessage) < 1:
        return {
            'statusCode': 200,
            'body': json.dumps(botMessage)
        }
        
    response = client.post_text(botName='DiningChatBoy',
        botAlias='bot',
        userId=user,
        inputText=lastUserMessage)
    
    if response['message'] is not None or len(response['message']) > 0:
        lastUserMessage = response['message']
    
    
    return {
        'statusCode': 200,
        'body': json.dumps(lastUserMessage)
    }