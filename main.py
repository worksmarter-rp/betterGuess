from urllib.parse import urlencode
import werkzeug.urls

# Older versions of :mod:`flask_wtf` relied on :func:`werkzeug.urls.url_encode`.
# This function was removed in Werkzeug 3 which ships in the current
# environment.  To keep the application working without pinning an older
# Werkzeug we provide a small compatibility shim before importing
# ``flask_wtf``.
if not hasattr(werkzeug.urls, "url_encode"):
    def _url_encode(obj, charset="utf-8", sort=False, key=None, separator="&"):
        return urlencode(obj)

    werkzeug.urls.url_encode = _url_encode

from flask import Flask, render_template, url_for, redirect, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from random import randint

app = Flask(__name__)
app.config['SECRET_KEY'] = '766584957-8;kjh'
Bootstrap(app)

class InputForm(FlaskForm):
    range = IntegerField("Guess a number 1 to what?", default=100)
    tries = IntegerField("How many Guesses?", default=8)
    submit = SubmitField("Let's Play!")

class NumberForm(FlaskForm):
    guess = IntegerField("", render_kw={"autofocus": True})
    submit = SubmitField("Submit your guess")

# helper for new games

def reset():
    session['game_range'] = 100
    session['game_tries'] = 8
    session['secret_number'] = randint(1, 100)
    session['attempts'] = 0
    session['game_state'] = 0
    session['guesses_over'] = []
    session['guesses_under'] = []
    session['guesses'] = []
    session['direction'] = ''
    session['last_guess'] = ''

def get_stats():
    return {
        "tries": session.get('game_tries', 8),
        "attempts": session.get('attempts', 0),
        "guesses": session.get('guesses', []),
        "guesses_under": session.get('guesses_under', []),
        "guesses_over": session.get('guesses_over', []),
        "secret": session.get('secret_number'),
        "game_state": session.get('game_state', 0),
        "direction": session.get('direction', ''),
        "guess": session.get('last_guess', ''),
        "session_hs": "",
        "game_range": session.get('game_range', 100),
    }

@app.route('/', methods=["GET", "POST"])
def new_game():
    reset()
    form = InputForm()
    if form.validate_on_submit():
        session['game_range'] = form.range.data
        session['game_tries'] = form.tries.data
        session['secret_number'] = randint(1, session['game_range'])
        session['game_state'] = 1
        return redirect(url_for('play_game'))
    return render_template('index.html', form=form)

@app.route('/play', methods=["GET", "POST"])
def play_game():
    if session.get('game_state', 0) < 1:
        return redirect(url_for('new_game'))
    if session.get('game_state') == 1:
        session['game_state'] = 2
    form = NumberForm()
    stats = get_stats()
    if session.get('game_state') in {4, 5}:
        return render_template('play_game.html', form=form, stats=stats), {
            'refresh': f'2; url="{url_for("new_game")}"'
        }
    if form.validate_on_submit():
        guess = form.guess.data
        stats['guess'] = guess
        session['last_guess'] = guess
        if guess in session['guesses'] or guess > session['game_range'] or guess < 1:
            session['game_state'] = 3
        else:
            session['attempts'] += 1
            if guess == session['secret_number']:
                session['game_state'] = 4
            elif session['attempts'] == session['game_tries']:
                session['game_state'] = 5
            elif guess > session['secret_number']:
                session['game_state'] = 2
                session['direction'] = 'smaller'
                session['guesses_over'].append(guess)
            else:
                session['game_state'] = 2
                session['direction'] = 'bigger'
                session['guesses_under'].append(guess)
            session['guesses'].append(guess)
        stats = get_stats()
        form.guess.data = None
        if session.get('game_state') in {4, 5}:
            return render_template('play_game.html', form=form, stats=stats), {
                'refresh': f'2; url="{url_for("new_game")}"'
            }
        return render_template('play_game.html', form=form, stats=stats)
    return render_template('play_game.html', form=form, stats=stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
