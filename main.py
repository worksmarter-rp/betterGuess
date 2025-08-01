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

from flask import Flask, render_template, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from random import randint

app = Flask(__name__)
app.config['SECRET_KEY'] = '766584957-8;kjh'
Bootstrap(app)

class InputForm(FlaskForm):
    range = IntegerField("Guess a number 1 to what?", default=100)
    tries = IntegerField("How many Guesses?", default=8)
    submit = SubmitField("Let's Play!")

class NumberForm(FlaskForm):
    guess = IntegerField("")
    submit = SubmitField("Submit your guess")

class PlayAgain(FlaskForm):
    submit = SubmitField("Play again?")

#SET DEFAULTS AND ESTABLISH VARIABLES
game_range = 100
game_tries = 8
secret_number = randint(1,100)
attempts = 0
game_state = 0
guesses_over = []
guesses_under = []
guesses = []
stats = {}
def reset():
    global game_range, game_tries, secret_number, attempts, game_state, guesses_over, guesses_under, guesses
    game_range = 100
    game_tries = 8
    secret_number = randint(1,100)
    attempts = 0
    game_state = 0
    guesses_over = []
    guesses_under = []
    guesses = []
reset()

#def var_check():
#    print(f'{game_range = }.  {game_tries = }, {secret_number = }')
@app.route('/', methods=["GET","POST"])
def new_game():
    reset()
    global game_range, game_tries, secret_number, game_state
    form = InputForm()
    #var_check()
    if form.validate_on_submit():
        game_range = form.range.data
        game_tries = form.tries.data
        secret_number = randint(1, game_range)
        game_state = 1

        #var_check()
        return redirect(url_for('play_game'))
    return render_template("index.html", form=form)
"""
Game states:
0 is game not initialized
1 is game initialized 
2 is game in play
3 is attempting the same guess
4 is game over win
5 is game over loss


"""
@app.route('/play', methods=["GET","POST"])
def play_game():
    form = NumberForm()
    global attempts, game_state, game_tries, guesses_over, guesses_under, guesses, secret_number, stats
    if game_state < 1:
        return redirect(url_for('new_game'))
    if game_state == 1:
        game_state = 2
        stats = {
            "tries": game_tries,
            "attempts": attempts,
            "guesses": [],
            "guesses_under": [],
            "guesses_over": [],
            "secret": secret_number,
            "game_state": game_state,
            "direction": "",
            "guess": "",
            "session_hs": "",
            "game_range":game_range
        }
    print(stats)

    if form.validate_on_submit():
        guess = form.guess.data
        print(stats)
        stats["guess"] = form.guess.data

        if guess in stats["guesses"] or guess > game_range or guess < 1:  #not a valid guess
            stats["game_state"] = 3
        else:
            attempts += 1
            stats["attempts"] = attempts
            if guess == secret_number:
                stats["game_state"] = 4
                return render_template('play_game.html', form=form, stats=stats), {"refresh": f'2; url="{url_for("new_game")}"'}
            elif attempts == game_tries:
                stats["game_state"] = 5
                return render_template('play_game.html', form=form, stats=stats), {
                    "refresh": f'2; url="{url_for("new_game")}"'}
            elif guess > secret_number:
                stats["game_state"] = 2
                stats["direction"] = "smaller"
                stats["guesses_over"].append(guess)
            elif guess < secret_number:
                stats["game_state"] = 2
                stats["direction"] = "bigger"
                stats["guesses_under"].append(guess)

            stats["guesses"].append(guess)
            print(stats)
        return render_template('play_game.html', form=form, stats=stats)

    return render_template('play_game.html', form=form, stats=stats)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')