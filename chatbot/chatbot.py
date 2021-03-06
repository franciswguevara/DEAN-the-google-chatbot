from chatbot.conversation import process_message, process_media
from chatbot.scraper import push, links, scraper, get_request, timeout
from chatbot.pymessenger_updated import Bot
from dotenv import load_dotenv
from flask import Flask, request
import functools
import json
import os
import random
import re
import pickle
import time

load_dotenv()

app = Flask(__name__)
ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)
df = {}
message_dict = {}
initial_message = {}
#Shoutout Maia
#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    #remember list of articles and what are article the user is reading
    global df
    global message_dict
    global initial_message

    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")

        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        if os.path.exists('df.pickle'):
            with open('df.pickle', 'rb') as x:
                df = pickle.load(x)

        with open('message.pickle', 'wb') as x:
            pickle.dump(message_dict, x, protocol=pickle.HIGHEST_PROTOCOL)

        # Get POST request sent to the bot
        output = request.get_json()
        print(output)

        # Get message details
        message = output['entry'][0]['messaging'][0]

        #Facebook Messenger ID for user so we know where to send response back to
        recipient_id = str(message['sender']['id'])
        
        message_dict[recipient_id] = message

        #If user sent a message
        if message.get('message'):
            
            #Stops message spam
            with open('message.pickle', 'rb') as x:
                previous_message = pickle.load(x)
                check_message = previous_message

            #Store recipient ID in previous message
            if check_message.get(recipient_id):
                pass
            else:
                initial_message[recipient_id] = {}
                previous_message = initial_message

            if message == previous_message[recipient_id]:
                print('STOP FUNCTION BEFORE IT SPAMS')
                return 'message processed'
            
            #If message is text
            if text := message['message'].get('text'):                            
                
                #Retrieve NLP analysis
                nlp = message['message'].get('nlp')
                
                if message['message'].get('quick_reply') == "registration":
                    quick_replies = [
                                        {
                                            "content_type":"user_email",
                                            "title": "E-Mail Address",
                                            "payload":"email",
                                        },{
                                            "content_type":"text",
                                            "title": "Main Menu",
                                            "payload":"menu"
                                        }
                                    ]
                    quick_reply_message(recipient_id,"Please share us the email attached to your Facebook Account to verify your membership",quick_replies)
                elif answer := process_message(text):
                    send_message(recipient_id,answer)
                elif text == 'Main Menu':
                    quick_replies = [
                                        {
                                            "content_type":"text",
                                            "title": "AJMA Member",
                                            "payload":"registration",
                                        },{
                                            "content_type":"text",
                                            "title": "External Partner",
                                            "payload":"partner"
                                        }
                                    ]
                    quick_reply_message(recipient_id, "Good Day! This is the Official Facebook Page of the Ateneo Junior Marketing Association. Please use any of the quick replies below to navigate.",quick_replies)
                else:
                    send_message(recipient_id,"What do you mean..When you nod your head yes but you wanna say no :(")
                return "Messaged Processed"
            #if user sends us a GIF, photo,video, or any other non-text item
            if message['message'].get('attachments'):
                #process_media(message['message'].get('attachments'))
                pass
                return "Messaged Processed"
        #If user clicked one of the postback buttons
        elif message.get('postback'):
            if message['postback'].get('title'):
                #If user clicks the get started button
                if message['postback']['title'] == 'Get Started':
                    quick_replies = [
                                        {
                                            "content_type":"text",
                                            "title": "AJMA Member",
                                            "payload":"registration",
                                        },{
                                            "content_type":"text",
                                            "title": "External Partner",
                                            "payload":"partner"
                                        }
                                    ]
                    quick_reply_message(recipient_id, "Good Day! This is the Official Facebook Page of the Ateneo Junior Marketing Association. Please use any of the quick replies below to navigate.",quick_replies)
                
        else:
            #gets triggered if there is another type of message that's not message/postback
            pass
    return "Message Processed"

def quick_reply_message(recipient_id,message,quick_replies):
    '''Send quick reply message to person'''
    bot.send_quick_replies(recipient_id,message,quick_replies)
    return "success"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'    

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    '''sends user the text message provided via input response parameter'''
    bot.send_text_message(recipient_id, response)
    return "success"

#uses PyMessenger to send message with button to user
def button_message(recipient_id,response,buttons):
    '''sends user the button message provided via input response parameter'''
    bot.send_button_message(recipient_id,response,buttons)
    return "success"

def feedback(recipient_id):
    '''Send a feedback button to let them provide feedback'''
    if random.random() <= 0.3:
        time.sleep(1.5)
        message = 'Thank you for using DEAN! If you have any comments or suggestions, let us know here! :)'
        buttons = [
                        {
                            "type":"postback",
                            "title":"Feedback",
                            "payload":recipient_id
                        }
                    ]
        button_message(recipient_id,message,buttons)
    return "success"

def timer(func):
    '''Print the Runtime of the decorated function'''
    @functools.wraps(func)
    def wrapper_timer(*args,**kwargs):
        start_time = time.perf_counter()
        value = func(*args,**kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer