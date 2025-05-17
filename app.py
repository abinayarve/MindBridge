import os
import re
import random
import requests
import spacy
import google.generativeai as genai
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Securely load API keys from environment variables
GEMINI_API_KEY = os.getenv("AIzaSyCSiOHQS-_ctcrUyjCd0rpIurbkP8vGWok")
PEXELS_API_KEY = os.getenv("JTqxbwKc9qOIXOJ2CMr2VJyW16vF1EnAaR1t1RriuFpYd4HryvMbqKzh")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Expanded Activities Themes
ACTIVITY_THEMES = [
    {
        "title": "Gentle Touch Exploration",
        "keywords": ["baby", "touch", "sensory", "soft"]
    },
    {
        "title": "Musical Bonding Journey",
        "keywords": ["baby", "music", "singing", "rhythm"]
    },
    {
        "title": "Mindful Breathing Connection",
        "keywords": ["baby", "calm", "breathing", "relaxation"]
    },
    {
        "title": "Nature Sounds Interaction",
        "keywords": ["baby", "nature", "sounds", "listening"]
    },
    {
        "title": "Gentle Movement Dance",
        "keywords": ["baby", "movement", "dance", "connection"]
    },
    {
        "title": "Texture Discovery Play",
        "keywords": ["baby", "textures", "learning", "exploration"]
    },
    {
        "title": "Emotional Mirroring Exercise",
        "keywords": ["baby", "emotions", "connection", "expression"]
    }
]

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Emergency keywords and helpline message
emergency_keywords = ["suicide", "kill", "end life", "die", "depressed"]
helpline_message = "🚨 If you're feeling overwhelmed, please reach out for help. You're not alone! 💖 Contact this emergency number: 988"

def generate_activity_description(theme):
    """Generate concise activity description"""
    prompt = f"Create a 5-point description for a baby bonding activity about {theme['title']}. Use clear, short bullet points focused on practical steps and emotional connection. Do not include stars or bullets in the response."
    
    try:
        response = model.generate_content(prompt)
        description = response.text.split('\n')[:5]
        return '\n'.join(description).replace('*', '').strip()  # Remove any remaining stars if present
    except Exception as e:
        return "1. Approach with love\n2. Be present\n3. Use gentle movements\n4. Maintain soft eye contact\n5. Breathe calmly together"

def fetch_activity_image(keywords):
    """Fetch relevant image from Pexels"""
    try:
        headers = {'Authorization': PEXELS_API_KEY}
        params = {
            'query': ' '.join(keywords),
            'per_page': 1,
            'orientation': 'square'
        }
        response = requests.get('https://api.pexels.com/v1/search', headers=headers, params=params)
        image_data = response.json()
        return image_data['photos'][0]['src']['large'] if image_data['photos'] else None
    except Exception as e:
        return "https://images.unsplash.com/photo-1532330393533-1a8494c6b1f5"

def classify_emotion(text):
    doc = nlp(text.lower())
    positive_keywords = ["happy", "joy", "love", "excited", "good", "great", "amazing"]
    negative_keywords = ["sad", "depressed", "angry", "upset", "bad", "frustrated", "unhappy"]

    positive_score = sum(1 for token in doc if token.text in positive_keywords)
    negative_score = sum(1 for token in doc if token.text in negative_keywords)

    if positive_score > negative_score:
        return "happy"
    elif negative_score > positive_score:
        return "sad"
    else:
        return "neutral"

def generate_ai_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        if response.text:
            return response.text.strip()
        else:
            return "I couldn't generate a response due to safety filters. Let's try something else!"
    except Exception as e:
        print(f"AI response error: {str(e)}")
        return "I encountered an error while generating a response. Please try again."

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_activity')
def get_activity():
    global ACTIVITY_THEMES
    if len(ACTIVITY_THEMES) == 0:
        # Restore original themes
        ACTIVITY_THEMES = [
            {
                "title": "Gentle Touch Exploration",
                "keywords": ["baby", "touch", "sensory", "soft"]
            },
            {
                "title": "Musical Bonding Journey",
                "keywords": ["baby", "music", "singing", "rhythm"]
            }
        ]
        
    
    # Select and remove a random theme
    theme = ACTIVITY_THEMES.pop(random.randint(0, len(ACTIVITY_THEMES)-1))
    
    # Generate description using Gemini
    description = generate_activity_description(theme)
    
    # Fetch image using Pexels
    image_url = fetch_activity_image(theme['keywords'])
    
    activity = {
        'title': theme['title'],
        'description': description,
        'image': image_url
    }
    
    return jsonify(activity)

@app.route('/bondingtime')
def bondingtime():
    return render_template('bondingtime.html')

@app.route('/hobbyquest')
def hobbyquest():
    return render_template('hobbyquest.html')

@app.route('/women')
def women():
    return render_template('women.html')

@app.route('/activity')
def activity():
    return render_template('activities.html')

@app.route('/calm_space')
def calm_space():
    return render_template('calmspace.html')

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/moodbooster')
def creative_wellness():
    return render_template('moodbooster.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)