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
    secret_number = 2
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
    if form.validate_on_submit():
        attempts += 1
        #var_check()
        guess = form.guess.data
        #print(f'{guess = }, you have used {attempts} out of {game_tries}. {game_tries-attempts} remain')
        game_status = f'you have used {attempts} out of {game_tries}. \n {game_tries-attempts} remain'
        if guess == secret_number:
            flash(f"You guessed my number of {secret_number} in {attempts} tries!")
            state_of_game = "won"
        elif guess > secret_number:
            direction = "smaller"
            guesses_over.append(guess)
        elif guess < secret_number:
            direction = "bigger"
            guesses_under.append(guess)
        if state_of_game != "won":
            flash(f"My number is {direction} than {guess}, \n {game_status} \n\n "
                  f"{guesses_over} were too big. \n {guesses_under} were too small")


        return render_template('play_game.html', form=form, guesses_over=guesses_over, guesses_under=guesses_under)
    return render_template('play_game.html', form=form)


if __name__ == "__main__":
    app.run()