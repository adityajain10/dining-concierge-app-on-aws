import boto3
import json

client = boto3.client('lex-runtime')


def lambda_handler(event, context):
    last_user_message = event['message'];
    botMessage = "Please try again.";
    # cognito = boto3.client('cognito-idp')
    print
    type(event);
    user = event['identityID']
    # access_token = str(event["id_token"]);
    # resp = cognito.get_user(
    # AccessToken=access_token
    # )
    # print("The cog "+access_token)

    # userattr = resp['UserAttributes']
    # email = ''
    # for val in userattr:
    #     if val['Name'] == 'email':
    #         email = val['Value']

    if last_user_message is None or len(last_user_message) < 1:
        return {
            'statusCode': 200,
            'body': json.dumps(botMessage)
        }

    response = client.post_text(botName='DiningChatBoy',
                                botAlias='bot',
                                userId=user,
                                inputText=last_user_message)

    if response['message'] is not None or len(response['message']) > 0:
        last_user_message = response['message']

    return {
        'statusCode': 200,
        'body': json.dumps(last_user_message)
    }
