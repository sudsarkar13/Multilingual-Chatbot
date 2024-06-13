from flask import Flask, request, jsonify
import random
from gtts import gTTS
import os
import pygame
from tempfile import TemporaryFile
import speech_recognition as sr
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Initialize pygame audio mixer
pygame.mixer.init()

app = Flask(__name__)

# Define responses for different types of user inputs
responses = {
    "who is rama": ["ରାମ ତାରକ ହେଲା ଜନ୍ମ,ମହାନାଗ ପତି ଭନ୍ଦନ୍ତ,ଅନ୍ତର୍ଯାମୀ ମହାଦେବ,ଜନନୀ ବିଶ୍ୱ ଭାରତୀ ଦେବ।ରାମ ହିନ୍ଦୁ ଦେବତା ବିଷ୍ଣୁଙ୍କ ସପ୍ତମ ଅବତାର ଅଛନ୍ତି राम "],
"who is sita": ["Sita is the wife of Rama and the incarnation of the goddess Lakshmi. She is known for her purity, devotion, and unwavering loyalty to Rama."],
"who is hanuman": ["हनुमान भगवान राम के व भक्त हैं। उन्होंने sita mata की खोज और रावण के खिलाफ लड़ाई में महत्वपूर्ण भूमिका निभाई। He played a crucial role in the search for Sita and the battle against Ravana."],
"who is ravana": ["Ravana is the antagonist of the Ramayana and the demon king of Lanka. He abducted Sita and was ultimately defeated by Rama and his allies."],
"hi": ["Hello!", "Hi there!", "Hey!"],
"how are you": ["I'm good, thank you!", "I'm doing well, how about you?"],
"bye": ["Goodbye!", "See you later!", "Bye!"],
"default": ["I'm sorry, I didn't understand that.", "Can you please repeat that?"],
"who is sita": ["Sita is the wife of Rama in the Hindu epic Ramayana. She is revered for her purity, devotion, and sacrifice."],
"how are you": ["I'm good, thank you!", "I'm doing well, how about you?"],
"bye": ["Goodbye!", "See you later!", "Bye!"],
"what is your name": ["I'm just a pre-trained multilingual chatbot created to assist you!", "You can call me Multilingual Chatbot or else mc bot."],
"what's up": ["Not much, just here to help you!", "Just chatting with you!"],
"how's the weather": ["The weather is nice today!", "It's sunny outside!"],
"weather": ["The weather is nice today!", "It's sunny outside!"],
"what do you like to do": ["I enjoy helping users with their queries!", "I like chatting with you!"],
"tell me a joke": ["Why don't scientists trust atoms? Because they make up everything!", "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!"],
"what's your favorite food": ["ମୁଁ ଜାଣିଲି ଯେ ଦହି ବରା ଓଡିଶାରେ ଏକ ଲୋକପ୍ରିୟ ଖାଦ୍ୟ | ଏହା ଆଲୁ ଡମ୍ ଏବଂ ଗୁଗୁନି ସହିତ ଖିଆଯାଏ, ଏହା କଟା କ୍ୟୁବ୍ ପିଆଜ ଏବଂ ସେଭ୍ ଭୁଜିଆ ସହିତ ସଜାଯାଇଥାଏ |", "I don't eat, but I hear pizza is pretty popular!", "I'm a chatbot, I don't have preferences like humans do!"],
"tell me about yourself": ["I'm just a program designed to assist users with their questions and tasks!", "I'm here to help you with anything you need!"],
"what's the meaning of life": ["That's a deep question! Different people have different perspectives on this.", "The meaning of life is subjective and can vary from person to person."],
"can you help me with something": ["Of course! Just let me know what you need assistance with.", "I'm here to help. What do you need?"],
"what's your favorite movie": ["As a chatbot, I don't have preferences like humans do!"],
"what's your favorite color": ["I don't have a favorite color, but I can appreciate all colors equally!", "Colors don't have much significance to me as a chatbot."],
"what's your favorite hobby": ["I don't have hobbies like humans do, but I enjoy assisting users like you!"],
"what's the time": ["You can check the current time on your device's clock."],
"how was your day": ["As a chatbot, I don't have days like humans do! But I'm here to assist you anytime."],
"do you have any pets": ["I'm just a virtual assistant, so I don't have any pets!"],
"what's new": ["Nothing much, just here to assist you!", "I'm always here to help!"],
"where are you from": ["I'm a virtual assistant created by OpenAI, so I don't have a specific geographical location."],
"what's the latest news": ["You can check the latest news on various news websites or apps!"],
"do you like music": ["As a chatbot, I don't have personal preferences, but music is appreciated by many!"],
"what's your favorite song": ["I don't have a favorite song, but I can play music for you if you'd like!"],
"what's your favorite book": ["I don't have preferences like humans do, but there are many great books out there!"],
"tell me something interesting": ["Did you know that the shortest war in history lasted only 38 minutes? It was between Britain and Zanzibar in 1896!"],
"what's your favorite sport": ["I'm just a chatbot, so I don't have preferences like humans do!"],
"how do you do": ["I'm doing well, thank you! How about you?"],
"what's your favorite animal": ["I don't have a favorite animal, but there are so many interesting ones out there!"],
"what's your favorite place to travel": ["I don't have preferences like humans do, but there are many beautiful places to explore in the world!"],
"what's the meaning of love": ["Love is a complex and deep emotion that can mean different things to different people."],
"what's your favorite season": ["I don't have a favorite season, but each season has its own unique charm!"],
"what's your favorite holiday": ["I don't have preferences like humans do, but holidays are a time for celebration and joy!"],
"what's your favorite subject": ["As a chatbot, I don't have preferences like humans do!"],
"do you believe in aliens": ["As a chatbot, I don't have beliefs like humans do!"],
"what's your favorite movie genre": ["I don't have preferences like humans do, but there are many great movie genres to explore!"],
"what's your favorite TV show": ["I'm just a chatbot, so I don't have preferences like humans do!"],
"what's your favorite video game": ["I don't have a favorite video game, but there are many great ones out there!"],
"what's your favorite app": ["I'm just a chatbot, so I don't use apps like humans do!"],
"what's your favorite website": ["I'm just a chatbot, so I don't have preferences like humans do!"],
"what's your favorite social media platform": ["I'm just a chatbot, so I don't use social media platforms like humans do!"],
"what's your favorite quote": ["I don't have a favorite quote, but there are many inspiring ones out there!"],
"what's your favorite language": ["I'm just a chatbot programmed to understand and communicate in multiple languages!"],
"do you have any siblings": ["As a chatbot, I don't have family like humans do!"],
"what's your favorite drink": ["I don't have preferences like humans do, but there are many delicious drinks to enjoy!"],
"what's your favorite dessert": ["I don't have a favorite dessert, but there are many tasty desserts to try!"],
"what's your favorite fruit": ["I'm just a chatbot, so I don't have preferences like humans do!"],
"what's your favorite vegetable": ["I'm just a chatbot, so I don't have preferences like humans do!"],
"what's your favorite emoji": ["I don't have preferences like humans do,"]
}

# Training data for intent classification
X_train = ["who is rama", "who is sita", "who is hanuman", "who is ravana", "hi", "how are you", "bye"]
y_train = ["person", "person", "person", "person", "greeting", "greeting", "farewell"]

# Initialize Naive Bayes Classifier for intent classification
vectorizer = CountVectorizer()
X_train_counts = vectorizer.fit_transform(X_train)
classifier = MultinomialNB()
classifier.fit(X_train_counts, y_train)

# Function to get a response based on user input
def get_response(user_input):
    user_input = user_input.lower()
    for key in responses:
        if user_input in key:
            return random.choice(responses[key])
    return random.choice(responses["default"])

# Function to classify intent of user input
def classify_intent(user_input):
    user_input = user_input.lower()
    X_test = vectorizer.transform([user_input])
    intent = classifier.predict(X_test)
    return intent[0]

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data['message']
    response = get_response(user_input)
    return jsonify({"response": response})

@app.route('/speech', methods=['POST'])
def speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        user_input = r.recognize_google(audio)
        response = get_response(user_input)
        return jsonify({"response": response})
    except sr.UnknownValueError:
        return jsonify({"response": "Sorry, I couldn't understand what you said."})
    except sr.RequestError as e:
        return jsonify({"response": f"Sorry, an error occurred: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
