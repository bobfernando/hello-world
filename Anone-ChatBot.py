import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import tkinter as tk
import spacy
import random
from datetime import date

#actions when program starts
def on_start():
    #show start messages
    start_msg = ["Greetings from the developer of this super simple chatbot.",
                 "Hopefully you can enjoy yourself with my cute little bot here.",
                 "Have a good time and stay positive!","",
                 "Anone : Good day. My name which my master bestowed upon me is Anone. Please refer to me as such."]
    for msg in start_msg:
        msg_list.insert(tk.END, msg)

    #get data from file containing replies
    #if no such file present then webscrape from the original source to create file
    global replies
    try:
        #get replies from Anone-reply.txt for use
        reply_file = open("Anone-reply.txt", encoding="utf-8")
        replies = [r.split("\t") for r in reply_file.readlines() if r!="\n" and r!=""]
        reply_file.close()
        
    except IOError:
        #get replies from web and write to Anone-reply.txt
        from bs4 import BeautifulSoup as soup
        from urllib.request import urlopen as uReq

        #getting replies from page 1
        page="https://www.coolnsmart.com/insult_quotes/"

        #request page 1 url
        uClient = uReq(page)
        
        #create soup object in html
        page_soup = soup(uClient.read(), "html.parser")
 
        #close page 1
        uClient.close()

        #get all div with class=entryq
        containers = page_soup.findAll("div", {"class":"entryq"})

        #open Anone-reply.txt for writing
        file = open("Anone-reply.txt", "w", encoding="utf-8")

        #write each reply in newline
        for i in range(len(containers)):
            file.write(containers[i].p.text.replace("\n", "\t"))
            file.write("\n")
            
        #getting replies from page 2-21
        for i in range(2,22):
            #new page url
            page_extension = "page/{}/".format(i)

            #request page url
            uClient = uReq(page+page_extension)

            #create soup object in html
            page_soup = soup(uClient.read(), "html.parser")

            #close page
            uClient.close()

            #get all div with class=entryq
            containers = page_soup.findAll("div", {"class":"entryq"})

            #write each reply in newline
            for i in range(len(containers)):
                file.write(containers[i].p.text.replace("\n", "\t"))
                file.write("\n")

        #close Anone-reply.txt for reading
        file.close()

        #get replies from Anone-reply.txt created
        reply_file = open("Anone-reply.txt", encoding="utf-8")

        #put content in replies for use
        replies = [r.strip().split("\t") for r in reply_file.readlines() if r!="\n" and r!=""]

        #close Anone-reply.txt
        reply_file.close()
        
#clear entry field for typing 
def start_type(event):
    my_msg.set("")
    
#default message for entry field
def end_type(event):
    if my_msg.get()=="":
        my_msg.set("Type your message here.")

#chat log for recording chat session
chat_log = []

#send message and clear entry field
def send(event=None):
    #get message if not empty and default help text
    if my_msg.get()!="" and my_msg.get()!="Type your message here.":
        msg = "You : " + my_msg.get()

        #display message
        msg_list.insert(tk.END, msg)

        #record to chat log
        chat_log.append(msg) 

        #reply chat message
        reply(my_msg.get()) 

        #clear entry field
        my_msg.set("")

#store name for user if detected while chatting
name = ""

#process entry messages for replying
def reply(msg):
    global name

    #load model for vocabulary, syntax, and entities in English
    nlp = spacy.load("en_core_web_sm")

    #tokenize and give tags to incoming message using spacy
    doc = nlp(msg)

    #detect name in message and add to variable for later use
    for ent in doc.ents:
        if ent.label_=="PERSON":
            name = " "+ent.text+". "
            break
      
    #tokenize entry message with nltk
    words = word_tokenize(msg)

    #make a list of stopwords in English 
    stop_words = stopwords.words("english")

    #remove stopwords from message 
    for w in words:
        if w in stop_words:
            words.remove(w)

    #list of words to trigger greet and end functions
    greetings = ["hey", "hello", "hi", "nice to meet you"]
    endings = ["bye", "quit", "goodbye", "byebye", "bye bye"]

    #decide which function to call for replying based on incoming message
    g = False
    e = False
    for w in words:
        if w.lower() in greetings:
            g = True
            break
        elif w.lower() in endings:
            e = True
            break
    if g:
        greet()
    elif e:
        end()
    else:
        main_reply(name)

#reply with greetings           
def greet():
    r = ["I am vegan.", "I have a boyfriend.", "Please mind your own business as I am not interested in you."]
    reply = "Anone : "+random.choice(r)
    msg_list.insert(tk.END, reply)
    chat_log.append(reply)

#reply with data extracted from Anone-reply.txt
def main_reply(name=""):
    global replies
    g = False
    #get reply
    rand_reply = random.choice(replies)

    #reply
    if len(rand_reply)>1:
        for r in rand_reply:
            reply = "Anone : {}".format(r)
            msg_list.insert(tk.END, reply)
    else:
        #add name to reply 
        for r in rand_reply:
            reply = "Anone : {}{}".format(name, r)
            msg_list.insert(tk.END, reply)
            
    #record to chat log       
    chat_log.append(reply) 


#end chat procedures  
def end():
    r = "I see you wish our time together to end, but I will never forget."
    reply = "Anone : "+r
    msg_list.insert(tk.END, reply)
    
    #record to chat log
    chat_log.append(reply)

    #removing interactive widgets
    entry_field.pack_forget()
    send_button.pack_forget()

    #create chat log file
    out_file_name = "Anone-"+date.today().isoformat()+".txt"
    out_file = open(out_file_name, 'w')
    for chat in chat_log:
        out_file.write(chat+"\n")
    out_file.close()
    
#GUI layout
root = tk.Tk()
root.title("Anone")

#frame for showing chat
msg_frame = tk.Frame(root)
yscrollbar = tk.Scrollbar(msg_frame)
xscrollbar = tk.Scrollbar(msg_frame, orient=tk.HORIZONTAL)

#list of messages on chat
msg_list = tk.Listbox(msg_frame, height=20, width=125,
                      yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)

#arrange widgets
yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
msg_frame.pack()

#variable for getting message
my_msg = tk.StringVar()
my_msg.set("Type your message here.")

#entry field
entry_field = tk.Entry(root, textvariable=my_msg, width=127)
entry_field.bind("<FocusIn>", start_type)
entry_field.bind("<FocusOut>", end_type)
entry_field.bind("<Return>", send)
entry_field.pack()

#send button
send_button = tk.Button(root, text="Send", command=send)
send_button.pack()

#on start actions
on_start()

root.mainloop()


