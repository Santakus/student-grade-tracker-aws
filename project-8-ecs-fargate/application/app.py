import random
from flask import Flask, jsonify

app = Flask(__name__)

QUOTES = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
    {"text": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
    {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"text": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
    {"text": "The best time to plant a tree was 20 years ago. The second best time is now.", "author": "Chinese Proverb"},
    {"text": "An unexamined life is not worth living.", "author": "Socrates"},
    {"text": "Spread love everywhere you go. Let no one ever come to you without leaving happier.", "author": "Mother Teresa"},
    {"text": "Tell me and I forget. Teach me and I remember. Involve me and I learn.", "author": "Benjamin Franklin"},
    {"text": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
    {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "The cloud is not someone else's computer. It's how you access someone else's computer.", "author": "Anonymous DevOps Engineer"},
    {"text": "There is no cloud, it's just someone else's computer.", "author": "AWS Student"},
]


@app.route('/')
def home():
    quote = random.choice(QUOTES)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quote of the Day</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            color: #f1f5f9;
            padding: 20px;
        }}
        .card {{
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 20px;
            padding: 50px 40px;
            max-width: 600px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        }}
        .emoji {{ font-size: 3rem; margin-bottom: 20px; }}
        h1 {{ font-size: 1.3rem; color: #818cf8; margin-bottom: 30px; font-weight: 600; }}
        .quote {{
            font-size: 1.4rem;
            font-weight: 300;
            line-height: 1.8;
            color: #e2e8f0;
            font-style: italic;
            margin-bottom: 20px;
        }}
        .author {{
            font-size: 1rem;
            color: #6366f1;
            font-weight: 600;
        }}
        .refresh {{
            display: inline-block;
            margin-top: 30px;
            padding: 12px 28px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: #fff;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s;
        }}
        .refresh:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(99,102,241,0.3); }}
        .footer {{
            margin-top: 40px;
            font-size: 0.8rem;
            color: #475569;
        }}
        .container-badge {{
            display: inline-block;
            margin-top: 10px;
            padding: 4px 12px;
            background: rgba(99,102,241,0.1);
            border: 1px solid rgba(99,102,241,0.2);
            border-radius: 50px;
            font-size: 0.7rem;
            color: #818cf8;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="emoji">✨</div>
        <h1>Quote of the Day</h1>
        <p class="quote">"{quote["text"]}"</p>
        <p class="author">— {quote["author"]}</p>
        <a href="/" class="refresh">🔄 New Quote</a>
    </div>
    <div class="footer">
        <p>Running on AWS ECS Fargate</p>
        <span class="container-badge">Container ID: {__import__("socket").gethostname()}</span>
    </div>
</body>
</html>'''


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/quote')
def api_quote():
    quote = random.choice(QUOTES)
    return jsonify(quote)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
