import geocoder
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import requests
import webbrowser as web
import os
import time
import playsound
from gtts import gTTS
import urllib.request
import re
import selenium.webdriver as sel_web
import subprocess
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pycaw.pycaw import AudioUtilities


def mute(mute):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session.SimpleAudioVolume
        if session.Process and mute == 'unmute':
            volume.SetMute(0, None)
        elif session.Process and mute == 'mute':
            volume.SetMute(1, None)

ibm_api_key = '1NCqK4M5985D926W54zVmj5JzSLMh6hHYaH-GWMeHd8n'

ibm_url = 'https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/f9cb7d0d-8212-408a-bc5f-eac8853f2574'

authenticator = IAMAuthenticator(ibm_api_key)
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)

text_to_speech.set_service_url(ibm_url)

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

weather_api = 'c692a0c7070e1a47184aba9ae86ca946'

# print(requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat=35&lon=139&appid={weather_api}"))

converter = pyttsx3.init()
voices = converter.getProperty('voices')

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = sel_web.Chrome(options=chrome_options, executable_path="D:\Downloads\chromedriver_win32\chromedriver.exe")

def jarvis_talk(text):
    with open('hello_world.mp3', 'wb') as audio_file:
        audio_file.write(
            text_to_speech.synthesize(
                text,
                voice="en-GB_JamesV3Voice",
                accept='audio/mp3'
            ).get_result().content)
        audio_file.close()
    playsound.playsound('hello_world.mp3')
    os.remove('hello_world.mp3')

def gspeak(text):
    tts = gTTS(text=text, lang="en", tld='co.uk')
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)

def old_talk(text):
    engine.say(text)
    engine.runAndWait()


def take_command():
    command = ''
    with sr.Microphone() as source:
        print('listening...')
        voice = listener.listen(source)
        try:
            command = listener.recognize_google(voice)
            command = command.lower()
            print("command", command)
            if 'jarvis' in command:
                command = command.replace('jarvis ', '')
        except sr.UnknownValueError:
            print("unknown words")
    return command


def run_jarvis(command):
    print(command)

    if 'play music' in command:
        song = command.replace('play ', '').strip(' ')
        jarvis_talk('playing ' + song)
        song_url = song.replace(' ', '+')
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + song_url)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        print("https://www.youtube.com/watch?v=" + video_ids[0])
        web.open("https://www.youtube.com/watch?v=" + video_ids[0])
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        jarvis_talk('Current time is ' + time)
    elif 'who is' in command:
        person = command.replace('who is ', '')
        try:
            info = wikipedia.summary(person, 1)
            jarvis_talk(info)
        except wikipedia.WikipediaException:
            jarvis_talk("person not found")
    elif 'what is' in command:
        object = command.replace('what is', '')
        try:
            info = wikipedia.summary(object, 1)
            jarvis_talk(info)
        except wikipedia.WikipediaException:
            jarvis_talk("I can't find a wikipedia article on that")
    elif 'to-do list' in command and 'read' in command:
        with open('to_do_list.txt', 'r') as my_file:
            lines = my_file.readlines()
            for line in lines:
                jarvis_talk(line)
            if len(lines) == 0:
                jarvis_talk("there's nothing to-do")
        my_file.close()
    elif 'add to my to-do list ' in command:
        command = command.replace('add to my to-do list ', '')
        with open('to_do_list.txt', 'a') as my_file:
            my_file.write(command)
            my_file.write('\n')
            my_file.close()
        jarvis_talk(f"I've added {command} to your to-do list")
    elif 'remove from my to-do list ' in command:
        command = command.replace('remove from my to-do list ', '')
        print(command)
        with open('to_do_list.txt', 'r') as my_file:
            with open("new_to_do_list.txt", "w") as output:
                for line in my_file:
                    if line.strip("\n") != command:
                        output.write(line)
                output.close()
            my_file.close()
        os.remove('to_do_list.txt')
        os.rename('new_to_do_list.txt', 'to_do_list.txt')
        jarvis_talk(f"I've removed {command} from your to-do list")
    elif 'weather' in command:
        lat, long = 52.68154, -1.82549
        resp = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={long}&APPID={weather_api}")
        # print(resp.json())
        forecast = resp.json()['daily'][0]
        today_weather = forecast['weather'][0]['description']
        # print(forecast)
        celsius = int(float(forecast['temp']['day'])-273)

        coat = ''
        if celsius <= 11:
            coat = 'a coat'
        elif celsius <= 14:
            coat = 'a light jacket'
        else:
            coat = 'no jacket'

        jarvis_talk(f"Today's weather is {today_weather} in Lichfield. The temperature is {celsius} degrees. You should wear {coat}.")
        # gspeak(f"Today's weather is {today_weather} in Lichfield. The temperature is {celsius} degrees.")
    elif 'status report' in command:
        with open('to_do_list.txt', 'r') as my_file:
            lines = my_file.readlines()
            plural = 's'
            if len(lines) == 1:
                plural = ''
            jarvis_talk(f"you have {len(lines)} item{plural} on your to-do list")
            my_file.close()
    elif 'search' in command:
        search = command.replace('search ', '')
        search = search.replace(' ', '+')
        url = f"https://www.google.com/search?q={search}"

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        search = soup.find_all('span', class_="aCOpRe")
        summary = search[0]
        print(summary.text)
        jarvis_talk(summary.text)
    elif 'are you there' in command:
        jarvis_talk("At your service.")
    elif 'share price' in command:
        search = command.replace('share price ', '')
        search = search.replace(' ', '+')
        url = f"https://www.google.com/search?q={search}"

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        search = soup.find_all('span', class_="IsqQVc NprOob XcVN5d wT3VGc")
        summary = search[0]
        jarvis_talk(summary.text)
    elif 'mute' in command:
        if 'unmute' in command:
            mute('unmute')
        else:
            mute('mute')


    # else:6
    #     old_talk('Please say the command again.')


while True:
    voice_data = take_command()
    run_jarvis(voice_data)