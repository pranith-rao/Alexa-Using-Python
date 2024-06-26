from __future__ import division
from typing import Text
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime,math
import wikipedia
import pyjokes
import requests,sys
import smtplib
import webbrowser,os
import smtplib,time,PyPDF2
import cv2
from requests import get
import pyautogui
import instaloader
import files.self_tweet as self_tweet
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from pyqt5_UI.start_page import Ui_Alexa
import operator
import psutil
import speedtest
from dotenv import load_dotenv

load_dotenv()

vscode_location = os.getenv('VSCODE_LOCATION')
weather_api_key = os.getenv('WEATHER_API_KEY')
news_api_key = os.getenv('NEWS_API_KEY')
email = os.getenv('EMAIL')
secret_key = os.getenv('SECRET_KEY')
receiver_whatsapp_number = os.getenv('RECEIVER_WHATSAPP_NUMBER')
whatsapp_message = os.getenv('WHATSAPP_MESSAGE')
time_in_24_hrs = int(os.getenv('TIME_IN_24_HRS'))
time_in_mins = int(os.getenv('TIME_IN_MINS'))


#text-to-speech converter
alexaa = pyttsx3.init('sapi5')                                                 
voices = alexaa.getProperty('voices')                                          #gets all voices
alexaa.setProperty('voice', voices[1].id)                                      #1 for female voice and 0 for male voice

#function that makes alexa speak
def talk(text):                                                                
    alexaa.say(text)                                                           #alexa's replies
    alexaa.runAndWait()

#function that makes alexa wish the user
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        talk("Good Morning!")
    elif hour>=12 and hour<18:
        talk("Good Afternoon!")   
    else:
        talk("Good Evening!")  
    talk("I am Alexa How can i help you?")  

#function to fetch 'C from the weather api
def weather(city): 
    api_key = weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name 
    response = requests.get(complete_url) 
    x = response.json()
    if x["cod"] != "404": 
        y = x["main"] 
        current_temperature = y["temp"]
        celsius = math.ceil(int(current_temperature) - 273.15)
        current_weather = x["weather"][0]["main"]
        details = [celsius,current_weather]
        return details


#function to send a email to someone
def sendEmail(to, content):                                                
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(email, secret_key)
    server.sendmail('youremail', to, content)
    server.close()


#function to fetch 5 headlines from news api
def news():
    main_url = 'http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=' + news_api_key
    fetched_news = requests.get(main_url).json()
    articles = fetched_news['articles']
    headlines = []
    day = ["first","second","third","fourth","fifth"]
    for ar in articles:
        headlines.append(ar["title"])
    for i in range(len(day)):
        print(f"Today's {day[i]} news is: {headlines[i]}")
        talk(f"Today's {day[i]} news is: {headlines[i]}")


#function to fetch current location from the api
def mylocation():
    try:
        ip_address = requests.get('https://api.ipify.org').text
        url = 'https://get.geojs.io/v1/ip/geo/'+ip_address+'.json'
        geo_requests = requests.get(url)
        geo_data = geo_requests.json()
        city = geo_data['city']
        country = geo_data['country']
        talk(f"I am not sure, but I think we are in {city} city of {country} country")
    except Exception as e:
        talk("Sorry, but due to network issues I am not able to track our location")
        pass


#function to read content of the pdf
def pdf_reader():
    pdf = open('files/The_Night_We_Met.pdf','rb')                                   #read binary
    pdfReader = PyPDF2.PdfFileReader(pdf)
    pages = pdfReader.numPages
    talk(f'Total number of pages in this pdf is {pages}')
    talk('Please enter the page number you want me to read')
    page_no = int(input("Enter the page number here: "))
    page_no = page_no - 1
    page = pdfReader.getPage(page_no)
    content = page.extractText()

    #to increase speech-speed
    time.sleep(1)
    talk('Please enter the number of words i have to read per minute')
    time.sleep(1)
    voiceRate = int(input("Enter the number of words to be read per minute(default is 200): "))
    time.sleep(1)
    alexaa.setProperty('rate',voiceRate)
    talk(content)
    alexaa.setProperty('rate',200)
    time.sleep(2)

    talk('Done, page finished')


#function to download instagram profile picture of anyone
def insta(self):
        talk("Please enter the correct user name")
        name = input("Enter insta ID here:")
        talk(f"Here is the innsta gram profile of {name}")
        webbrowser.open(f"www.instagram.com/{name}")
        time.sleep(3)
        talk("Would you like to download the profile picture of this account?")
        print("Would you like to download the profile picture of this account? Type Yes or No")
        reply = input()
        reply = reply.lower()
        if "yes" in reply:
            instagram = instaloader.Instaloader()
            instagram.download_profile(name, profile_pic_only = True)
            talk("Done, profile picture has been saved")
        else:
            talk("OK")
            pass

#setting edge as the browser to open sites
webbrowser.register('edge',None,
	webbrowser.BackgroundBrowser("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"))


class MainThread(QThread):
    def __init__(self):
        super(MainThread,self).__init__()

    def run(self):
        self.TaskExecution()

    def take_command(self):                                                     #function to take commands from users
        listener = sr.Recognizer()                                              #speech recognizer
        with sr.Microphone() as source:                                         #our microphone will be used as source to take commands
            print('Alexa is listening...')                                      #indication that alexa is ready
            listener.adjust_for_ambient_noise(source)  
            listener.pause_threshold = 1
            voice = listener.listen(source,timeout=6,phrase_time_limit=5)       #alexa listens to your command
        try:
            print("Recognizing...")
            command = listener.recognize_google(voice,language='en-in')         #your command is converted into text using google api
            command = command.lower()
            print(f"You said: {command}")
        except Exception as e:
            print("Sorry I dont know that")
            return "None"
        return command


    def TaskExecution(self):
        while True:                                                                          #alexa in sleep mode initially
            print("Please wake me up by saying 'Alexa wake up' to continue")
            self.permission = self.take_command()
            if 'wake up' in self.permission:
                wishMe()
                while True:
                    self.command = self.take_command()

                    #list of functions alexa can perform
                    #greeting functions
                    if 'who are you' in self.command:
                        talk("I'm Alexa, a desktop assistant built by Pranith")
                    elif 'how are you' in self.command:
                        talk("I'm fine. How are you?")
                    elif "i am fine" in self.command:
                        talk("Glad to hear that. How can I help you?")
                    elif 'are you single' in self.command:
                        talk("Yes, but to be honest, I don't think so.")
                    elif 'do you love me' in self.command:
                        talk("Yes, and only because you’re enjoying it.")

                    #basic questions
                    elif 'the time' in self.command:                                         #if time is asked
                        now_time = datetime.datetime.now().strftime('%I:%M %p')              #time is converted into string using strftime() %I is 12-hour clock %M is minutes %p is am or pm
                        talk('Current time is ' + now_time)
                    elif 'date' in self.command:
                        date = datetime.date.today().strftime("%B %d, %Y")              #month,day,year
                        talk('Todays date is'+ str(date))
                    elif 'joke' in self.command:
                        joke = pyjokes.get_joke()
                        print(joke)
                        talk(joke)
                    elif 'weather' in self.command:
                        try:
                            city = str(self.command.split("in",1)[1]).lower().lstrip()
                            weather_api = weather(city)
                            current_weather = weather_api[1]
                            temperature = weather_api[0]
                            talk('Weather in' + city +'is'+ str(current_weather) + "and" + 'temperature is' + str(temperature) + 'degree celsius')
                        except:
                            talk("Sorry but can you please specify the place you want to know the weather of?")
                    elif "where am i" in self.command or "what is my location" in self.command or "where are we" in self.command:
                        talk("Let me check.")
                        mylocation()
                    elif 'internet speed' in self.command or 'net speed' in self.command:
                        talk("OK let me check")
                        talk("Please give me 2 minutes")
                        net_details = speedtest.Speedtest()
                        downloadSpeed = int(net_details.download()/1000000)
                        uploadSpeed = int(net_details.upload()/1000000)
                        result_message = f'Your download speed is {downloadSpeed} MB per second and your upload speed is {uploadSpeed} MB per second'
                        print(result_message)
                        talk(result_message)
                    elif "ip address" in self.command:
                        ip = get('https://api.ipify.org').text
                        print(f"Your IP address is {ip}")
                        talk(f"Your IP address is {ip}") 
                    
                    #tasks to be done on edge
                    elif 'play' in self.command:                                               #command to play song
                        song = self.command.replace('play', '')                              #play is removed from command so that we get the song name
                        talk('playing ' + song)                                              #alexa will inform us which song is being played
                        talk('Going to sleep wake me up again')
                        pywhatkit.playonyt(song)
                        break                                             #song will be played on youtube
                    elif 'open youtube' in self.command:
                        talk("Opening youtube")
                        talk('Going to sleep wake me up again')
                        webbrowser.get('edge').open("youtube.com")
                        break
                    elif 'open google' in self.command:
                        talk("What should I search on google?")
                        try:
                            search = self.take_command().lower()
                        except:
                            talk("Please repeat it again")
                            search = self.take_command().lower()
                        talk("Fetching your results from google")
                        webbrowser.get('edge').open(f"google.com/search?q={search}")
                    elif 'open stack overflow' in self.command:
                        talk("Opening stack overflow")
                        talk('Going to sleep wake me up again')
                        webbrowser.get('edge').open("https://stackoverflow.com/")
                        break
                    
                    #fetching data
                    elif 'who is' in self.command:
                        try:
                            person = self.command.split("who is",1)[1]                       #command will be trimmed to only the subject name after who is 
                            person = str(person)
                            info = wikipedia.summary(person, 1, auto_suggest=False)          #alexa will go through wikipedia and tell us about it. 1 specifies no.of statemets you want about the subject
                            print(f"According to Wikipedia: {info}")
                            talk(info)
                        except:
                            talk("Sorry no results found")
                    elif 'wikipedia' in self.command:
                        talk('Searching Wikipedia..')
                        try:
                            self.command = self.command.replace("wikipedia", "")
                            info = wikipedia.summary(self.command, 1, auto_suggest=False)
                            talk("According to wikipedia")
                            print(f"According to Wikipedia: {info}")
                            talk(info)
                        except:
                            talk("Sorry no results found")
                    elif "news" in self.command:
                        talk("Fetching today's latest news")
                        news()
                    elif "pdf" in self.command:
                        pdf_reader()                                                        #alexa will read the pdf mentioned in the function

                    #control applications in windows
                    elif 'open code' in self.command:
                        talk("Opening visual studio code")
                        vs_path = vscode_location
                        os.startfile(vs_path)
                    elif "close code" in self.command:
                        talk("Closing visual studio code")
                        os.system("taskkill /f /im Code.exe")
                    elif 'open command prompt' in self.command:
                        os.system("start cmd")
                    elif "open camera" in self.command:
                        print("Press esc to close camera")
                        cap = cv2.VideoCapture(0)
                        while True:
                            ret ,img = cap.read()
                            cv2.imshow('webcam', img)
                            k = cv2.waitKey(50)
                            if k == 27:
                                break
                        cap.release()
                        cv2.destroyAllWindows()
                    elif "open notepad" in self.command:
                        talk("Opening notepad")
                        np_path = "C:\\Windows\\system32\\notepad.exe"
                        os.startfile(np_path)
                    elif "close notepad" in self.command:
                        talk("Closing notepad")
                        os.system("taskkill /f /im notepad.exe")

                    #automate social networks
                    elif 'send an email' in self.command:
                        try:
                            talk("Please enter the mail ID of the person you want to email")
                            to = input()                                                      #email ID of the person you want to send the mail
                            talk("Please enter the content of the mail")
                            print("After entering the content press enter to send")
                            print("Please enter the content of the mail:")
                            content = input()   
                            sendEmail(to, content)
                            talk("Email has been sent!")
                        except Exception as e:
                            print(e)
                            talk("Sorry! I am not able to send this email")
                    elif 'send whatsapp message' in self.command:
                        #At the time specified, message will be sent to the phone number entered
                        #eg:+(countrycode)1234567890
                        pywhatkit.sendwhatmsg(receiver_whatsapp_number,whatsapp_message,time_in_24_hrs,time_in_mins)            #(number with country code,message,hours in 24-format,minutes)                    
                        talk("Message has been sent")
                    elif "instagram profile" in self.command or "profile on instagram" in self.command:
                        insta(self)
                    elif "tweet" in self.command or "twitter" in self.command:
                        #have your twitter cerdentials saved in twitter_info.txt file
                        talk("Please enter what you want to tweet?")
                        print("Please enter what you want to tweet?")
                        tweet = input().capitalize()
                        if tweet == 'none':
                            talk("tweet can't be empty")
                            continue
                        else:
                            try:
                                self_tweet.tweet(tweet)
                                talk("Done, Tweeted successfully!")
                            except:
                                talk("Tweet failed")
                                pass
                    
                    #basic windows functions
                    elif 'switch the window' in self.command:
                        pyautogui.keyDown("alt")
                        pyautogui.press("tab")
                        time.sleep(1)
                        pyautogui.keyUp("alt")
                    elif "take a screenshot" in self.command or  "screenshot the screen" in self.command:
                        talk("In what name the screenshot must be saved?")
                        name = self.take_command().lower()
                        talk("Leave the screen idle for 3 seconds")
                        time.sleep(3)
                        screenshot = pyautogui.screenshot()
                        screenshot.save(f"{name}.png")
                        talk("Done, screenshot is captured")
                    elif "hide all files" in self.command or "hide this folder" in self.command:  
                        os.system("attrib +h /s /d")
                        talk("All the files in the current directory are hidden")
                    elif "visible to everyone" in self.command:
                        talk("Are you sure?")
                        reply = self.take_command().lower()
                        if "yes" in reply:
                            os.system("attrib -h /s /d")
                            talk("All the files in the current directory are visible to everyone now")
                        else:
                            talk("Ok, Files untouched")
                    elif 'battery' in self.command:
                        battery = psutil.sensors_battery()
                        percentage = battery.percent
                        talk(f"Your system battery percentage is {percentage}")

                    #control volume of system
                    elif 'volume up' in self.command:
                        pyautogui.press('volumeup')
                    elif 'volume down' in self.command:
                        pyautogui.press('volumedown')
                    elif 'unmute' in self.command or 'mute' in self.command:
                        pyautogui.press('volumemute')

                    #control power options of system
                    elif "shut down the system" in self.command:
                        talk("Shutting down")
                        os.system("shutdown /s /t 5")
                    elif "restart the system" in self.command:
                        talk("Restarting")
                        os.system("shutdown /r /t 5")
                    elif "the system into sleep" in self.command:
                        talk("Sleep mode ON")
                        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

                    #other functions
                    #avoided voice recognition for this as it was taking numbers as words and operators as words
                    #1000 as thousand sometimes and / as divided. So to avoid this taking input was better 
                    elif "do some calculations" in self.command or "can you calculate" in self.command:
                        talk("Please enter the question you want me to calculate.")
                        print("Keep space between operands and operator. Eg: 2 ** 2")
                        command = input("Enter your question: ")                                           
                        def get_operator_fn(op):
                            return{
                                '+': operator.add,                
                                '-': operator.sub,                
                                '*': operator.mul,               
                                '/': operator.truediv,
                                '**': operator.pow,
                                '%':operator.mod,     
                            }[op] 
                        def eval_binary_expr(op1,oper,op2):
                            op1,op2 = int(op1), int(op2)
                            return get_operator_fn(oper)(op1, op2)
                        try:
                            print(f"The result is {eval_binary_expr(*(command.split()))}")
                            talk(f"The result is {eval_binary_expr(*(command.split()))}")
                        except:
                            print("Sorry invalid question")
                            talk("Sorry invalid question")

                    #birthday wish with a pencil sketch of the image             
                    elif 'birthday' in self.command:
                        talk("Sure")
                        talk("Happieee Birthday")
                        img = cv2.imread('static/Bday_Pic.jpg')
                        print(img)
                        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        inverted_gray_image = 255 - gray_image
                        blurred_img = cv2.GaussianBlur(inverted_gray_image, (21,21), 0)
                        inverted_blurred_img = 255 - blurred_img
                        pencil_sketch = cv2.divide(gray_image, inverted_blurred_img, scale=256.0)
                        #cv2.imshow('Original Image',img)
                        cv2.imshow('Happy Birthday',pencil_sketch)
                        cv2.waitKey(0)


                    #alexa control functions
                    elif 'sleep' in self.command:
                        talk("Going to sleep")
                        talk("Just say Alexa wake up to wake me up")
                        break
                    elif 'stop' in self.command or 'thank you' in self.command:
                        talk("Thank you for using me. Goodbye!")
                        sys.exit()
                    else:
                        talk('Sorry I dont know that')
            elif 'stop' in self.permission or 'thank you' in self.permission:
                talk("Thank you for using me. Goodbye!")
                sys.exit()

startExecution = MainThread()

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Alexa()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.startTask)          #when start btn is clicked run startTask function
        self.ui.pushButton_2.clicked.connect(self.close)            #when close btn is clicked close the window

    def startTask(self):
        self.ui.movie = QtGui.QMovie("static/alexa.gif")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)            
        timer.start(1000)
        startExecution.start()

    def showTime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString("hh:mm:ss")
        label_date = current_date.toString(Qt.ISODate)
        self.ui.textBrowser.setText(label_date)                #display date in frontend
        self.ui.textBrowser_2.setText(label_time)              #display time in frontend

app = QApplication(sys.argv)
alexa = Main()
alexa.show()
sys.exit(app.exec_())



