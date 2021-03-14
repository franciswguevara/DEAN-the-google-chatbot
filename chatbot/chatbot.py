from chatbot.conversation import generator, processor
from chatbot.pymessenger_updated import Bot
from dotenv import load_dotenv
from flask import Flask, request
import functools
import json
import os
import random
import pickle
import time

load_dotenv()

app = Flask(__name__)
ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)
memory = {}

class response:
    def __init__(self, output, memory):
        #User Information
        
        
        #Declare attributes
        self.message = output['entry'][0]['messaging'][0]
        self.memory = memory
        self.uid = str(self.message['sender']['id'])

        self.dict = None
        self.nlp = None
        self.reply = None
        self.text = None

        self.no_repeat()
        self.user_info()

    def user_info(self):
        '''Retrieve user information'''
        fields = ['id','name','first_name','last_name','profile_pic']
        user = bot.get_user_info(self.uid,fields)
        self.name = user['name']
        self.first_name = user['first_name']
        self.last_name = user['last_name']
        self.picture = user['profile_pic']

    def no_repeat(self):
        '''Stops message spam'''
        with open('message.pickle', 'wb') as x:
            pickle.dump(self.memory, x, protocol=pickle.HIGHEST_PROTOCOL)   

        with open('message.pickle', 'rb') as x:
            past_memory = pickle.load(x)
        if past_memory.get(self.uid):
            if self.message == past_memory[self.uid]:
                return 'Message Processed'
        
        self.memory[self.uid] = self.message
        
    
    def send_message(self):
        bot.send_quick_replies(self.uid,self.reply,self.dict)
        return "Message Processed"

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():

    global memory

    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)

    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # Get POST request sent to the bot
        output = request.get_json()
        print(output)

        # Get message details
        message = response(output,memory)
        processor(message)
        return "Message Processed"

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'    

# def feedback(recipient_id):
#     '''Send a feedback button to let them provide feedback'''
#     if random.random() <= 0.3:
#         time.sleep(1.5)
#         message = 'Thank you for using DEAN! If you have any comments or suggestions, let us know here! :)'
#         buttons = [
#                         {
#                             "type":"postback",
#                             "title":"Feedback",
#                             "payload":recipient_id
#                         }
#                     ]
#         button_message(recipient_id,message,buttons)
#     return "success"

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