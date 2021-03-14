import re

class generator:
    '''Generates the dictionary for quick reply options'''
    def __init__(self):
        self.dict = []
    
    def add_property(self,title,payload,content='text'):
        '''Add quick reply buttons'''
        temp_dict = {
            'content_type': content,
            'title': title,
            'payload': payload
        }
        self.dict.append(temp_dict)
    
    def preset_menu(self,name=''):
        '''Preset Menus to choose from'''
        if name == 'member':
            self.add_property('Retention Status','retention')
            self.add_property('Events','events')
        elif name == 'email':
            self.add_property('user_email','E-Mail Address','email')
        elif name == 'menu':
            self.add_property('AJMA Member','member')
            self.add_property('External Partner','partner')
        elif name == 'partner':
            pass
        
        if name != 'menu':
            self.add_property('Menu','menu')

class processor:
    def __init__(self,response):
        '''Handles the sorting of type of message'''
        message = response.message
        #message
        if message := message.get('message'):
            #text
            if temp := message.get('text'):
                response.text = temp
                #quick reply
                if temp := message.get('quick_reply'):
                    response.payload = temp['payload']
                    return self.quick_reply(response)
                #normal text
                else:
                    response.nlp = message.get('nlp')
                    return self.text(response)
            #photo or video    
            if temp := message.get('attachments'):
                response.attachments = temp
                return self.attachments(response)
        #postback response
        elif temp := message.get('postback'):
            response.title = temp['title']
            return self.postback(response)
        #don't understand how this will get triggered
        else:
            factory = generator()
            response.reply = "Wow, how did you do that?"
            factory.preset_menu()
            response.dict = factory.dict
            response.send_message()
            return 
    
    def quick_reply(self,response):
        '''Handles the sorting of type of quick reply'''
        payload = response.payload
        factory = generator()

        if payload == 'member':
            #If the member is registered na
            # if response.uid:
            #     pass
            # else:
            factory.preset_menu('email')
            response.reply('Email?')
        elif re.search(r"^[a-z0-9\._]+[@]\w+[.]\w+",payload):
            factory.preset_menu('member')
            response.reply = 'Email Yay'
        elif payload == 'retention':
            factory.preset_menu('member')
            response.reply = 'Retention Yay'
        elif payload == 'events':
            factory.preset_menu('member')
            response.reply = 'Events Yay'
        elif payload == 'partner':
            factory.preset_menu('partner')
            response.reply = 'Partner Yay'
        elif payload == 'menu':
            factory.preset_menu('menu')
            response.reply = 'Menu Yay'
        response.dict = factory.dict
        response.send_message()

    def postback(self,response):
        title = response.title 
        factory = generator()
        if title == 'Get Started':
            response.reply = 'Happy Sunday!'
            factory.preset_menu('menu')
        response.dict = factory.dict
        response.send_message()

    def text(self,response):
        '''Understand what they said'''
        text = response.text
        text = text.lower().strip()
        factory = generator()

        #match
        greetings = ['hi','hello']
        gratitude = 'thank'

        if any(re.search(re.compile(f'\\b{x}\\b'),text) for x in greetings):
            response.reply = "Hello there!"
        elif re.search(gratitude,text):
            response.reply = "You're welcome! :)"
        else:
            response.reply = "I don't understand :("

        factory.preset_menu()
        response.dict = factory.dict
        response.send_message()

    def attachments(self, response):
        '''Do something with attachments'''
        response.reply = "Wow that's a nice pic/vid!"
        factory = generator()
        factory.preset_menu()
        response.dict = factory.dict
        response.send_message()