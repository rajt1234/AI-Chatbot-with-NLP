# ===== Importing Necessary Libraries =====
import spacy                       # For natural language processing tasks (e.g., parsing, lemmatization).
import speech_recognition as sr    # For capturing and converting voice to text.
import webbrowser                  # To open websites in the default browser.
import pyttsx3                     # For converting text to speech (offline TTS).
import musicLibrary                # Custom module to map song names to URLs.
import requests                    # To make HTTP API requests (e.g., weather, news).
import json                        # For handling JSON data from APIs.
from openai import OpenAI          # To interact with the OpenAI/OpenRouter AI API.
from datetime import datetime      # To format and handle date/time values (e.g., sunrise/sunset).
from dotenv import load_dotenv     # To load API keys and environment variables from a `.env` file.
import os                          # To access environment variables and system functions.

load_dotenv()   # I used this command to load environment variables from a .env file into my python environment.

# ===== This code captures voice input and speaks responses aloud using the speak() function.=====
recognizer = sr.Recognizer()
engine = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")

def speak(text):
    print(f"Dhruva: {text}")
    engine.say(text)
    engine.runAndWait()

# ===== This function gets a AI response from an AI model based on the user's command.=====
def aiProcess(command):
    client = OpenAI(
        base_url=os.getenv("Openrouter_URL"),   # Replace with your actual AI model base_url
        api_key=os.getenv("AI_API_KEY"),        # Replace with your actual AI Model API key.
    )
    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",    # Name your model according to will.I have used 'deepseek-r1-0528' AI model because it is free.
        messages=[{"role": "user", "content": command}]
    )
    return completion.choices[0].message.content

# ===== This function tells the current weather of a given city using OpenWeatherMap.=====
def get_weather(city):
    weather_api_key = os.getenv("Weather_API")       # Replace with your actual weather API. I have used OpenWeatherMap API key because it is free.
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"  # Replace with your actual weather url.

    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            weather = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            temp_min = data["main"]["temp_min"]
            temp_max = data["main"]["temp_max"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind_speed = data["wind"]["speed"]
            wind_deg = data["wind"].get("deg", "N/A")
            cloudiness = data["clouds"]["all"]
            sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%I:%M %p')
            sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%I:%M %p')

            weather_report = (
                f"Weather in {city.capitalize()}: {weather}. "
                f"Temperature is {temp}°C, feels like {feels_like}°C. "
                f"Min temperature {temp_min}°C, max temperature {temp_max}°C. "
                f"Humidity is {humidity}%, pressure is {pressure} hPa. "
                f"Wind is blowing at {wind_speed} m/s, direction {wind_deg}°. "
                f"Cloudiness is {cloudiness}%. "
                f"Sunrise at {sunrise}, sunset at {sunset}."
            )
            speak(weather_report)
        else:
            speak(f"Sorry, I couldn't get the weather for {city}.")
    except Exception as e:
        speak(f"An error occurred while fetching weather data: {e}")

# ===== This function handles commands to open social media sites, play music, get news, fetch weather, or chat with AI.=====
def processCommand(c):
    c = c.lower()
    doc = nlp(c)
    lemmas = [token.lemma_ for token in doc]
    command_text = " ".join(lemmas)

    # ***** Here,the below command tells us about current weather of the given/provided location.*****
    if "weather in" in c or "weather at" in c or "today's weather in" in c:
         # Extracting city name
        if "weather in" in c:
            city = c.split("weather in")[-1].strip()
        elif "weather at" in c:
            city = c.split("weather at")[-1].strip()
        elif "today's weather in" in c:
            city = c.split("today's weather in")[-1].strip()
        get_weather(city)
        return

    # ***** Here,the below commands open secial media sites and a search engine.*****
    if "google" in lemmas and "open" in lemmas:
        webbrowser.open("https://google.com")
    elif "facebook" in lemmas:
        webbrowser.open("https://facebook.com")
    elif "instagram" in lemmas:
        webbrowser.open("https://instagram.com")
    elif "youtube" in lemmas:
        webbrowser.open("https://youtube.com")
    elif "linkedin" in lemmas:
        webbrowser.open("https://linkedin.com")
    elif "twitter" in lemmas:
        webbrowser.open("https://twitter.com")

    # ***** Here,the below command open's music in youtube. You can change platform by updating links in musicLibrary.py *****
    elif "play" in lemmas:
        for i, token in enumerate(doc):
            if token.lemma_ == "play":
                song = doc[i+1:].text.strip()
                if song in musicLibrary.music:
                    webbrowser.open(musicLibrary.music[song])
                else:
                    speak("Sorry, I couldn't find that song.")
                return

    # ***** Here,the below command tell us about news.*****
    elif "news" in lemmas:
        news_api_key = os.getenv("News_API")     # Replace with your actual News API.
        #  You can change country according to your choice i.e <country=in> for India.
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}")   # Replace with your actual news url.
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            if articles:
                for article in articles[:5]:
                    speak(article['title'])
            else:
                speak("Sorry, I couldn't find any news articles right now.")
        else:
            speak("Failed to fetch the news. Please try again later.")

    # ===== Below command is executed if none of the command satisfies i.e command fall back to AI =====
    else:
        output = aiProcess(c)
        speak(output)

# ===== This function listens for the wake word "Dhruva" and processes voice commands.=====
def voice_mode():
    speak("Initializing Dhruva in voice mode....")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Adjusted for ambient noise. Waiting for wake word...")

        while True:
            try:
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                word = recognizer.recognize_google(audio)
                print(f"You said: {word}")

                if word.lower() == "dhruva":
                    speak("Yes?")
                    print("Listening for command...")
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=7)
                    command = recognizer.recognize_google(audio)
                    print(f"Command: {command}")
                    processCommand(command)
            except sr.WaitTimeoutError:
                print("Listening timed out. Waiting again...")
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

# ===== This function handles text commands until "exit" is typed.=====
def typing_mode():
    speak("Initializing Dhruva in typing mode....")
    print("Type 'exit' to quit typing mode.")
    while True:
        command = input("You: ")
        if command.lower() == "exit":
            speak("Exiting typing mode. Goodbye!")
            break
        processCommand(command)

# ===== This code lets the user pick and run voice or typing mode.=====
if __name__ == "__main__":
    speak("Welcome! Choose mode: 1 for voice, 2 for typing")
    choice = input("Enter 1 for voice mode or 2 for typing mode: ").strip()
    if choice == "1":
        voice_mode()
    elif choice == "2":
        typing_mode()
    else:
        speak("Invalid choice. Exiting program.")