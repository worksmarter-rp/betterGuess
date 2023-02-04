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
    guess = IntegerField("What is your guess")
    submit = SubmitField("Submit your guess")

class PlayAgain(FlaskForm):
    submit = SubmitField("Play again?")

#SET DEFAULTS AND ESTABLISH VARIABLES
def reset():
    global game_range, game_tries, secret_number, attempts, state_of_game, guesses_over, guesses_under
    game_range = 100
    game_tries = 8
    secret_number = randint(1,100)
    attempts = 0
    state_of_game = "setup"
    guesses_over = []
    guesses_under = []
reset()

#def var_check():
#    print(f'{game_range = }.  {game_tries = }, {secret_number = }')
@app.route('/', methods=["GET","POST"])
def new_game():
    reset()
    global game_range, game_tries, secret_number
    form = InputForm()
    #var_check()
    if form.validate_on_submit():
        game_range = form.range.data
        game_tries = form.tries.data
        secret_number = randint(1, game_range)
        #var_check()
        return redirect(url_for('play_game'))
    return render_template("index.html", form=form)

@app.route('/play', methods=["GET","POST"])
def play_game():
    form = NumberForm()
    global attempts, state_of_game
    stats = {
        "tries": game_tries,
        "attempts": 0,
        "guesses": [],
        "guesses_under": guesses_under,
        "guesses_over": guesses_over,
        "secret": secret_number,
        "game_state": 0,
    }
    if form.validate_on_submit():
        attempts += 1
        if attempts > game_tries:
            stats = {
                "tries": game_tries,
                "attempts": 0,
                "guesses": [],
                "guesses_under": guesses_under,
                "guesses_over": guesses_over,
                "secret": secret_number,
                "game_state": -1,
            }
            return render_template('play_game.html', form=form, stats=stats), {"refresh": f'4; url="{url_for("new_game")}"'}

        guess = form.guess.data


        game_status = f'you have used {attempts} out of {game_tries}. \n {game_tries-attempts} remain'
        if guess == secret_number:
            flash(f"You guessed my number of {secret_number} in {attempts} tries!")
            game_state = 1
            direction = "equal"
        elif guess > secret_number:
            game_state = 2
            direction = "smaller"
            guesses_over.append(guess)
        elif guess < secret_number:
            game_state = 3
            direction = "bigger"
            guesses_under.append(guess)
        stats = {
            "tries": game_tries,
            "attempts": attempts,
            "guesses": [].append(guess),
            "guesses_under": guesses_under,
            "guesses_over": guesses_over,
            "secret": secret_number,
            "game_state": game_state,
            "direction": direction,
            "guess":guess
        }
        return render_template('play_game.html', form=form, stats=stats)

    return render_template('play_game.html', form=form, stats=stats)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')