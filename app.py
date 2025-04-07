from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Gemini
genai.configure(api_key=app.config['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-2.0-flash')

def is_pet_related(question):
    """Check if question is pet-related using Gemini"""
    prompt = f"""Is this question about pet care? Answer only 'yes' or 'no':
    Question: {question}"""
    try:
        response = model.generate_content(prompt)
        return "yes" in response.text.lower()
    except:
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    pet_type = data.get('pet_type', 'pet')
    
    if not user_message:
        return jsonify({'response': 'Please enter a valid question.'})
    
    # Check if question is pet-related
    if not is_pet_related(user_message):
        return jsonify({'response': 'I specialize only in pet care advice.'})
    
    try:
        prompt = app.config['SYSTEM_PROMPT'].format(pet_type=pet_type) + user_message
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': 'Sorry, I encountered an error. Please try again.'})

if __name__ == '__main__':
    app.run(debug=True)