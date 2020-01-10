# Dining-Concierge-Chat-App
This is a serverless, micro service-driven web application created completely using AWS cloud services. The main application of this chatbot is to provide restaurant suggestions to its users based on the preferences provided to it through conversations.

It is basic chat-bot application to interect with open APIs. We are focusing on popular use cases for the interaction and getting the real time data. As a user you will chat with amazon lex bot and get real time answers with the suggestion and recommandation.

We have support for Yelp-API with suggestions and real time chat. <br/>

## Services Used
1. Amazon S3 - To host the frontend
2. Amazon Lex - To create the bot
3. API Gateway - To set up the API
4. Amazon SQS - to store user requests on a first-come bases
5. ElasticSearch Service - To quickly get restaurant ids based on the user preferences of cuisine collected from SQS
6. DynamoDB - To store the restaurant data collected using Yelp API
7. Amazon SNS - to send restaurant suggestions to users through SMS
8. Lambda - To send data from the frontend to API and API to Lex, validation, collecting restaurant data, sending suggestions using SNS.
9. Yelp API - To get suggestions for food
10. AWS Congito - For authentication


## Chat Architecture Diagram
![diagram](architecture_diagram.png)


## Chat sneak peek
![snap](chat-front.png)


## Chat Example
![example](chat_example.png)
