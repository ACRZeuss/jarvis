from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import time
import speech_recognition as sr
import pyttsx3
import pytz
import subprocess
import time
from datetime import datetime as day_name
from datetime import date
import webbrowser
import pyautogui

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_EXTENSIONS = ["nd", "rd", "th", "st"]

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 120)
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""
        
        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))
            
    return said.lower()

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(day, service):
    # Call Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = date.today()

    if text.count("today") > 0:
        return today
    
    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year = year + 1

    if day < today.day and month == -1 and day != -1:
        month = month + 1

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7
                
        return today + datetime.timedelta(dif)
    if day != -1:    
        return datetime.date(month=month, day=day, year=year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    notepad = "C:/Program Files/Notepad++/notepad++.exe"
    subprocess.Popen([notepad, file_name])


WAKE = "hey jarvis"
SERVICE = authenticate_google()
print("Start")
speak("hello sir")

while True:
    print("Listening")
    text = get_audio()

    if text.count(WAKE) > 0:
        speak("I am listening to you sir")
        text = get_audio()

        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]

        for phrase in CALENDAR_STRS:
            if phrase in text.lower():
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("I don't understand")

        NOTE_STRS = ["make a note", "write this down", "remember this"]

        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down?")
                note_text = get_audio()
                note(note_text)
                speak("I've made a note of that.")

        NAME_STRS = ["what is your name", "what's your name"]
        
        for phrase in NAME_STRS:
            if phrase in text:
                speak("my name is jarvis sir")

        CHR_STRS = ["open chrome"]
        
        for phrase in CHR_STRS:
            if phrase in text:
                speak("i am opening")
                chrome = "C:/Program Files/Google/Chrome/Application/chrome.exe"
                subprocess.Popen([chrome])

        OPR_STRS = ["open opera"]
        
        for phrase in OPR_STRS:
            if phrase in text:
                speak("i am opening")
                opera = "C:/Users/erhan/AppData/Local/Programs/Opera GX/launcher.exe"
                subprocess.Popen([opera])
        
        CLOCK_STRS = ["what time is it"]
        
        for phrase in CLOCK_STRS:
            if phrase in text:
                t = time.localtime()
                current_time = time.strftime("%H:%M", t)
                speak(current_time)

        DAY_STRS = ["what day is it today"]
        
        for phrase in DAY_STRS:
            if phrase in text:
               
                speak(today)

        DATE_STRS = ["what is today's date", "what's today's date", "today's date"]
        
        for phrase in DATE_STRS:
            if phrase in text:
                today = day_name.today().strftime("%A")
                date = date.today()
                speak(today)
                speak(date)

        EXIT_STRS = ["exit", "see you later"]

        for phrase in EXIT_STRS:
            if phrase in text:
                speak("see you later sir")
                exit()

        SEARCH_GOOGLE_STRS = ["search google"]

        for phrase in SEARCH_GOOGLE_STRS:
            if phrase in text:
                speak("what do you want me to search")
                search = get_audio()
                print(search)
                url = "https://www.google.com/search?q={}".format(search)
                webbrowser.get().open(url)
                speak("i am listing the ones i could google for {}.".format(search))

        # SEARCH_YT_STRS = ["search youtube"]

        # for phrase in SEARCH_YT_STRS:
        #     if phrase in text:
        #         speak("what do you want me to search")
        #         search = get_audio()
        #         print(search)
        #         url = "https://www.youtube.com/results?search_query={}".format(search)
        #         webbrowser.get().open(url)
        #         speak("i am listing the ones i could youtube for {}.".format(search))

        OPEN_YT_CH_STRS = ["open my youtube channel"]

        for phrase in OPEN_YT_CH_STRS:
            if phrase in text:
                speak("i am opening")
                url = "https://www.youtube.com/channel/UCSK5fEs-xHV1NfNRPg6F20w"
                webbrowser.get().open(url)

        SAY_HELLO_STRS = ["say hello", "say hi"]

        for phrase in SAY_HELLO_STRS:
            if phrase in text:
                speak("hello")

        SONG_CONTROL_STRS = ["start music", "pause music"]

        for phrase in SONG_CONTROL_STRS:
            if phrase in text:
                pyautogui.press('playpause')

        VOL_DOWN_STRS = ["volume down"]

        for phrase in VOL_DOWN_STRS:
            if phrase in text:
                pyautogui.press('volumedown')

        VOL_UP_STRS = ["volume up"]

        for phrase in VOL_UP_STRS:
            if phrase in text:
                pyautogui.press('volumeup')

        PREV_TRACK_STRS = ["previous track"]

        for phrase in PREV_TRACK_STRS:
            if phrase in text:
                pyautogui.press('prevtrack')

        NEXT_TRACK_STRS = ["next track"]

        for phrase in NEXT_TRACK_STRS:
            if phrase in text:
                pyautogui.press('nexttrack')
