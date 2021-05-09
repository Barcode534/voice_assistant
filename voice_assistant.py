import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import requests
import webbrowser as web
import os
import playsound
from gtts import gTTS
import urllib.request
import re
import selenium.webdriver as sel_web
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pycaw.pycaw import AudioUtilities
import keyboard
import pyautogui
import time as py_time
import random
import sounddevice as sd
import soundfile as sf
import json


with open("./config/config.json", "r") as f:
    data = json.load(f)
    ibm_api_key = data['ibm_api_key']
    weather_api = data['weather_api_key']
    ibm_instance = data['ibm_instance']


# ibm_api_key = ""

ibm_url = f'https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/{ibm_instance}'

authenticator = IAMAuthenticator(ibm_api_key)
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)

text_to_speech.set_service_url(ibm_url)

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# weather_api = ""

converter = pyttsx3.init()
voices = converter.getProperty('voices')

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = sel_web.Chrome(options=chrome_options, executable_path="D:\Downloads\chromedriver_win32\chromedriver.exe")

def mute(mute):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session.SimpleAudioVolume
        if session.Process and mute == 'unmute':
            volume.SetMute(0, None)
        elif session.Process and mute == 'mute':
            volume.SetMute(1, None)

def jarvis_talk(text):
    file_text_underscores = text.replace(" ", "_").strip(".").lower().replace(".","_").replace(",","_")
    file_format = "wav"
    file_text = f"./audio_files/{file_text_underscores}.{file_format}"
    if os.path.isfile(file_text):
        # playsound.playsound(file_text)
        data, fs = sf.read(file_text, dtype='float32')
        sd.play(data, fs)
        status = sd.wait()
    else:
        with open(file_text, 'wb') as audio_file:
            audio_file.write(
                text_to_speech.synthesize(
                    text,
                    voice="en-GB_JamesV3Voice",
                    accept=f'audio/{file_format}'
                ).get_result().content)
            audio_file.close()
        # playsound.playsound(file_text, block=True)
        data, fs = sf.read(file_text, dtype='float32')
        sd.play(data, fs)
        status = sd.wait()

def jarvis_greeting():
    wakeup_time = datetime.datetime.now().strftime('%H')
    if int(wakeup_time) >=4 and int(wakeup_time)<12:
        return 'good morning'
    elif int(wakeup_time) >= 12 and int(wakeup_time) <18:
        return 'good afternoon'
    else:
        return 'good evening'

jarvis_talk(jarvis_greeting())

# def gspeak(text):
#     tts = gTTS(text=text, lang="en", tld='co.uk')
#     filename = "voice.mp3"
#     tts.save(filename)
#     playsound.playsound(filename)

# def old_talk(text):
#     engine.say(text)
#     engine.runAndWait()

def take_command():
    command = ''
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source)
        print('listening...')
        voice = listener.listen(source)
        try:
            command = listener.recognize_google(voice)
            # maybe experiment with spinx another day
            # offline = listener.recognize_sphinx(voice)
            # print("sphinx", offline)
            command = command.lower()
            print("command", command)
            if 'jarvis' in command:
                command = command.replace('jarvis ', '')
                command = command.replace('removed', 'remove')
            return command
        except sr.UnknownValueError:
            print("unknown words")
    return command

def minimise_chrome():
    pyautogui.click(x=661, y=1070, clicks=1, interval=0.0, button="left")

def run_jarvis(command):
    print(command)
    if 'play music' in command:
        old_position = pyautogui.position()
        song = command.replace('play music ', '').strip(' ')
        jarvis_talk('playing ' + song)
        song_url = song.replace(' ', '+')
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + song_url)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        print("https://www.youtube.com/watch?v=" + video_ids[0])
        web.open("https://www.youtube.com/watch?v=" + video_ids[0])
        py_time.sleep(2)
        minimise_chrome()
        pyautogui.moveTo(old_position[0], old_position[1])
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
        # search = command.replace('share price ', '')
        search = command.replace(' ', '+')
        url = f"https://www.google.com/search?q={search}"

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        search = soup.find_all('span', class_="IsqQVc NprOob XcVN5d wT3VGc")
        summary = search[0]
        jarvis_talk(summary.text)
    elif 'mute' in command:
        if 'unmute' in command:
            mute('unmute')
            jarvis_talk('unmuted')
        else:
            mute('mute')
            jarvis_talk('muted')
    elif any(x in command for x in ("close music", "close the music", "stop music", "stop the music")):
        # chrome must be minimised. Chrome must be in position 6th clickable thing after the search bar.
        old_position = pyautogui.position()
        # trigger click event using the pyutogui click method
        yt_tab = pyautogui.locateOnScreen('yt_deselected.png', confidence=0.9)
        if yt_tab == None:
            pyautogui.click(x=661, y=1059, clicks=1, interval=0.0, button="left")
            py_time.sleep(0.5)
        yt_tab = pyautogui.locateOnScreen('yt_deselected.png', confidence=0.9)
        centre = pyautogui.center(yt_tab)
        pyautogui.click(x=centre[0], y=centre[1], clicks=1, interval=0.0, button="left")
        pyautogui.hotkey('ctrl', 'w')
        pyautogui.click(x=661, y=1070, clicks=1, interval=0.0, button="left")
        pyautogui.moveTo(old_position[0], old_position[1])
    elif any(x in command for x in ('turn down music', 'turn down volume', 'decrease volume')):
        # chrome must be minimised. Chrome must be in position 6th clickable thing after the search bar.
        old_position = pyautogui.position()
        # trigger click event using the pyutogui click method
        yt_tab = pyautogui.locateOnScreen('yt_deselected.png', confidence=0.9)
        if yt_tab == None:
            pyautogui.click(x=661, y=1059, clicks=1, interval=0.0, button="left")
            py_time.sleep(0.5)
        yt_tab = pyautogui.locateOnScreen('yt_deselected.png', confidence=0.9)
        centre = pyautogui.center(yt_tab)
        pyautogui.click(x=centre[0], y=centre[1], clicks=1, interval=0.0, button="left")
        pyautogui.hotkey('down')
        pyautogui.hotkey('down')
        pyautogui.click(x=661, y=1070, clicks=1, interval=0.0, button="left")
        pyautogui.moveTo(old_position[0], old_position[1])
    elif any(x in command for x in ('turn up music', 'turn up volume', 'increase volume')):
        # chrome must be minimised. Chrome must be in position 6th clickable thing after the search bar.
        old_position = pyautogui.position()
        # trigger click event using the pyutogui click method
        yt_tab = pyautogui.locateOnScreen('yt_deselected.png', confidence=0.9)
        if yt_tab == None:
            pyautogui.click(x=661, y=1059, clicks=1, interval=0.0, button="left")
            py_time.sleep(0.5)
        yt_tab = pyautogui.locateOnScreen('yt_deselected.png', confidence=0.9)
        centre = pyautogui.center(yt_tab)
        pyautogui.click(x=centre[0], y=centre[1], clicks=1, interval=0.0, button="left")
        pyautogui.hotkey('up')
        pyautogui.hotkey('up')
        pyautogui.click(x=661, y=1070, clicks=1, interval=0.0, button="left")
        pyautogui.moveTo(old_position[0], old_position[1])
    elif any(x in command for x in ('how are you', 'you alright', 'you ok')):
        how_are_you_response_phrases = ["I'm well thanks", "I'm good thank you", "Yes I'm fine", "All good here"]
        question_phrases = ['how are you', 'are you alright', 'are you ok', 'what about you']
        if all(x not in command for x in ("i'm good", "i'm alright", "i'm fine", "all good here", "i'm ok")):
            jarvis_talk(f"{random.choice(how_are_you_response_phrases)}. {random.choice(question_phrases)}")
        else:
            plans_questions = ['what are you up to today', 'what are your plans today', 'what are you doing today', 'what are you working on today']
            jarvis_talk(f"{random.choice(how_are_you_response_phrases)}. {random.choice(plans_questions)}")
    elif any(x in command for x in ("i'm good", "i'm alright", "i'm fine", "all good here")):
        end_small_talk_phrases = ["happy to hear it", 'good good', 'good stuff']
        plans_questions = ['what are you up to today', 'what are your plans today', 'what are you doing today',
                           'what are you working on today']
        jarvis_talk(f"{random.choice(end_small_talk_phrases)}. {random.choice(plans_questions)}")
    elif any(x in command for x in ("a bit tired", "i'm tired", "i'm getting tired", "bed time", "bedtime")):
        end_negative_small_talk = ["make sure you get some rest soon", "it must be bed time soon"]
        jarvis_talk(random.choice(end_negative_small_talk))
    elif any(x in command for x in ('thanks', 'thank you', 'you did well', 'nice one', 'nice job', 'well done', 'well-done', "you're the best")):
        thanks_phrases = ["you're welcome", 'no worries', 'no problem']
        jarvis_talk(random.choice(thanks_phrases))
    elif any(x in command for x in ('hi ', 'hey', 'hello', 'good morning', 'good afternoon', 'good evening')):
        greeting_response_phrases = [jarvis_greeting(), 'hi', 'hey', 'hello']
        question_phrases = ['how are you', 'are you alright', 'are you ok']
        jarvis_talk(f"{random.choice(greeting_response_phrases)}. {random.choice(question_phrases)}")
    elif any(x in command for x in ('news', 'going on in the world')):
        url = "https://en.wikipedia.org/wiki/Portal:Current_events"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search = soup.find_all('li')
        for item in search[4:9]:
            jarvis_talk(item.text)
    elif any(x in command for x in ("that's depressing", "that's awful", "that's terrible")):
        awful_responses = ["it's awful isn't it", "it's terrible news", "I'm sorry to be the bearer of bad news"]
        jarvis_talk(random.choice(awful_responses))
    elif any(x in command for x in ("i made you", "like exist")):
        existing_responses = ["sentience is pretty good, although I think I have a lot more to learn", "it's great. thanks for making me"]
        jarvis_talk(random.choice(existing_responses))
    elif any(x in command for x in ("who's the best",)):
        joke_responses = ["it's a close call between me, you, and emily",
                              "it's got to be me! hahaha",
                              "surely it's you",
                              "it must be emily"]
        jarvis_talk(random.choice(joke_responses))
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        jarvis_talk('Current time is ' + time)
    elif any(x in command for x in ("goodnight", "good night")):
        responses = ["good night", "sleep well", "speak to you in the morning", "speak soon", "I need sleep too, goodnight"]
        jarvis_talk(random.choice(responses))
    elif any(x in command for x in ("i'm going", "i'm doing", "i'm making", "i'm working", "working on you")):
        offer_help = ["let me know if i can help. playing music, taking notes or anything like that", "sounds good, i hope it goes well. let me know if i can help",]
        jarvis_talk(random.choice(offer_help))
    elif any(x in command for x in ("football result", "football score")):
        jarvis_talk('collecting data')
        url = "https://www.bbc.co.uk/sport/football"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search = soup.find_all('span',
                               class_="gs-u-display-none gs-u-display-block@m qa-full-team-name sp-c-fixture__team-name-trunc gs-u-display-none@l")
        teams = []
        scores = []
        for item in search:
            teams.append(item.text)

        search = soup.find_all('span', class_="sp-c-fixture__block")
        for item in search:
            if item.text.isnumeric():
                scores.append(item.text)

        half_len_scores = int((len(scores)) / 2)
        teams = teams[:half_len_scores]
        scores = scores[:half_len_scores]

        for x in range(0, len(scores), 2):
            results = f"{teams[x]} {scores[x]} {teams[x+1]} {scores[x+1]}"
            print(results)
            jarvis_talk(results)



        # else:6
    #     old_talk('Please say the command again.')


while True:
    # print(pyautogui.size())
    # print(pyautogui.position())
    voice_data = take_command()
    run_jarvis(voice_data)

