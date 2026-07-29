from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# Word list for different categories
word_list = {
    'Fruits': ['apple', 'banana', 'cherry', 'grape', 'mango', 'orange', 'pineapple', 'kiwi', 'watermelon'],
    'Countries': ['canada', 'brazil', 'india', 'china', 'germany', 'japan', 'spain', 'france', 'australia'],
    'Cricketers': ['sachin', 'kohli', 'babar', 'smith', 'warne', 'ponting', 'tendulkar', 'dhoni', 'gilly'],
    'Footballers': ['messi', 'ronaldo', 'neymar', 'mbappe', 'hazard', 'lewandowski', 'salah', 'debruyne'],
    'Vegetables': ['carrot', 'broccoli', 'spinach', 'lettuce', 'potato', 'tomato', 'cucumber', 'eggplant'],
    'Foods': ['pizza', 'burger', 'sushi', 'pasta', 'salad', 'steak', 'noodles', 'icecream', 'cupcake']
}

# Hangman stages (images)
hangman_images = [
    'hangman_0.png',  # No body parts guessed (fully alive)
    'hangman_1.png',  # Head
    'hangman_2.png',  # Head + Body
    'hangman_3.png',  # Head + Body + 1 arm
    'hangman_4.png',  # Head + Body + 2 arms
    'hangman_5.png',  # Head + Body + 2 arms + 1 leg
    'hangman_6.png',  # Head + Body + 2 arms + 2 legs (game over)
]

# Game state for each player
game_state = {}

# Funny jokes for the game
jokes = [
    "Why don't skeletons fight each other? They don't have the guts!",
    "I told my computer I needed a break. Now it won’t stop sending me Kit-Kats!",
    "Why don’t some couples go to the gym? Because some relationships don’t work out!",
    "I used to play piano by ear, but now I use my hands.",
    "Did you hear about the mathematician who’s afraid of negative numbers? He will stop at nothing to avoid them!"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    username = request.form['username']
    category = random.choice(list(word_list.keys()))  # Randomly select category
    word = random.choice(word_list[category])  # Select a random word from that category
    game_state[username] = {
        'word': word,
        'category': category,
        'guessed_letters': [],
        'attempts_left': 6,
        'word_placeholder': ['_'] * len(word),
        'message': "Let's play! Guess the word letter by letter.",
        'score': 0,
        'new_word_count': 0,
        'hint_chances': 3,  # User has 3 chances to use hints
        'popup_title': '',
        'popup_message': '',
        'sarcastic_joke': ''
    }
    return render_template('game.html', username=username, game_state=game_state[username], hangman_image=hangman_images[0], joke=random.choice(jokes))

@app.route('/guess', methods=['POST'])
def guess():
    username = request.form['username']
    guess = request.form['guess'].lower()

    if guess in game_state[username]['guessed_letters']:
        game_state[username]['message'] = "You already guessed that letter. Try again!"
    elif guess in game_state[username]['word']:
        game_state[username]['guessed_letters'].append(guess)
        for i in range(len(game_state[username]['word'])):
            if game_state[username]['word'][i] == guess:
                game_state[username]['word_placeholder'][i] = guess
        if '_' not in game_state[username]['word_placeholder']:
            game_state[username]['message'] = f"🎉 Congratulations {username}! You guessed the word! 🎉"
            game_state[username]['score'] += 10
            game_state[username]['popup_title'] = "You Win!"
            game_state[username]['popup_message'] = f"Bravo, {username}! You nailed it! But now, what's next? 🤔"
            game_state[username]['sarcastic_joke'] = "Wow, you actually guessed it. Don’t get too cocky though."
        else:
            game_state[username]['message'] = "Good guess! Keep going! 😊"
    else:
        game_state[username]['guessed_letters'].append(guess)
        game_state[username]['attempts_left'] -= 1
        if game_state[username]['attempts_left'] == 0:
            game_state[username]['message'] = f"😢 You lost! The correct word was: {game_state[username]['word']} 😢 Better luck next time! 😎"
            game_state[username]['popup_title'] = "Game Over!"
            game_state[username]['popup_message'] = f"Oops! You lost. But hey, there’s always next time. 😜"
            game_state[username]['sarcastic_joke'] = "Well, that was predictable. I guess you're just too good at losing."
        else:
            game_state[username]['message'] = "Oops! That was a wrong guess. Try again!"
    
    # Update hangman image based on attempts left
    hangman_image = hangman_images[6 - game_state[username]['attempts_left']]
    joke = random.choice(jokes)

    return render_template('game.html', username=username, game_state=game_state[username], hangman_image=hangman_image, joke=joke)

@app.route('/hint', methods=['POST'])
def hint():
    username = request.form['username']
    if game_state[username]['hint_chances'] > 0:
        word = game_state[username]['word']
        hint_letter = random.choice([i for i in range(len(word)) if game_state[username]['word_placeholder'][i] == '_'])
        game_state[username]['word_placeholder'][hint_letter] = word[hint_letter]
        game_state[username]['hint_chances'] -= 1  # Decrease hint chances
        return render_template('game.html', username=username, game_state=game_state[username], hangman_image=hangman_images[6 - game_state[username]['attempts_left']], joke=random.choice(jokes))
    else:
        game_state[username]['message'] = "You have no hint chances left! 😕"
        hangman_image = hangman_images[6 - game_state[username]['attempts_left']]
        return render_template('game.html', username=username, game_state=game_state[username], hangman_image=hangman_image, joke=random.choice(jokes))

@app.route('/scoreboard')
def scoreboard():
    scores = sorted([(user, state['score']) for user, state in game_state.items()], key=lambda x: x[1], reverse=True)
    return render_template('scoreboard.html', scores=scores)

@app.route('/go_home', methods=['POST'])
def go_home():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
