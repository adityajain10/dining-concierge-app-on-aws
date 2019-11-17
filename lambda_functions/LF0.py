def lambda_handler(event, context):
    
    lastUserMessage = event['message'];
    botMessage = "Please try again.";
    
    if lastUserMessage is None or len(lastUserMessage) < 1:
        return {
            'statusCode': 200,
            'body': json.dumps(botMessage)
        }
    
    response = client.post_text(botName='DiningChatBoy',
        botAlias='bot',
        userId='test',
        inputText=lastUserMessage)
    
    if response['message'] is not None or len(response['message']) > 0:
        lastUserMessage = response['message']
    
    
    return {
        'statusCode': 200,
        'body': json.dumps(lastUserMessage)
    }