from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
import random
import pandas as pd
from wildcard_mask import generate_question_from_csv, ask_question

headers = ["128", "64", "32", "16", "8", "4", "2", "1"]
decimal_guess = pd.DataFrame(columns=['Random Binary', 'Correct Decimal', 'User Guess', 'Result'])
binary_guess = pd.DataFrame(columns=['Random Decimal', 'Correct Binary', 'User Guess', 'Result'])
wildcardmak_results = pd.DataFrame(columns=['Random Question, Correct Answer', 'User Guess', 'Result'])

app= Flask(__name__)
app.secret_key = 'theonekey'


@app.route('/')
def main():
    return render_template('main.html')


@app.route("/decimal-to-binary", methods=['GET', 'POST'])
def decimal_to_binary():
    # Generate a new decimal-binary pair if the request is GET (page load) and not in session
    if request.method == 'GET' or 'random_binary' not in session:
        random_decimal = random.randint(0, 255)
        random_binary = format(random_decimal, '08b')
        session['random_binary'] = random_binary  # Store binary value in session
        session['random_decimal'] = random_decimal  # Store decimal value in session
        session['counter'] = 0
        session['game_over'] = False
    else:
        # Retrieve the values from the session for POST (submission)
        random_binary = session.get('random_binary')
        random_decimal = session.get('random_decimal')

    result = None  # Default result for initial load

    # Process the form submission (POST request)
    if request.method == 'POST':
        user_guess = request.form['user_guess']
        try:
            
            # Ensure user's guess is in binary format
            if not all(bit in '01' for bit in user_guess) or len(user_guess) != 8:
                raise ValueError("Invalid binary input.")
            
            # Validate the guess
            if user_guess == random_binary:
                result = f"Congratulations! You've guessed the correct answer of {random_binary}" 
                session['game_over'] = True
            elif session['counter'] >= 2:
                result = f"Sorry, you've used all 3 tries! The correct answer was {random_binary}."
                session['game_over'] = True  # Set game over to True
            else:
                result = f"Incorrect!. Please try again"
            session['counter'] += 1
            
            # Log results to CSV
            binary_guess.loc[len(binary_guess)] = [random_binary, random_decimal, user_guess, result]
            binary_guess.to_csv('decimal_to_binary_results.csv', index=False)

            
        except ValueError:
            result = "Invalid input. Please enter an 8-bit binary number."

    # Render template with the random decimal and result message
    return render_template('decimaltobinary.html', 
                           random_decimal=random_decimal, 
                           random_binary=session.get('random_binary'),
                           result=result, 
                           headers=headers, game_over=session['game_over'] )


@app.route("/binary-to-decimal", methods=['GET', 'POST'])
def binary_to_decimal():
        # Generate a new decimal-binary pair if the request is GET (page load)
    if request.method == 'GET' or 'random_decimal' not in session:
        random_decimal = random.randint(0, 255)
        random_binary = format(random_decimal, '08b')
        session['random_decimal'] = random_decimal  # Store decimal value in session
        session['counter'] = 0
        session['game_over'] = False
    else:
        # Retrieve the values from the session for POST (submission)
        random_decimal = session.get('random_decimal')
        random_binary = format(random_decimal, '08b')
        

    result = None  # Default result for initial load
    correct = None
    

    # Process the form submission (POST request)
    if request.method == 'POST':
        user_guess = request.form['user_guess']
        try:
            # Convert user's guess to an integer
            user_guess = int(user_guess)
            # Validate the guess
            
            if user_guess == random_decimal:
                result = f"Congratulations! You've guessed the correct answer of {random_decimal}" 
                session['game_over'] = True
            elif session['counter'] >= 2:
                result = f"Sorry, you've used all 3 tries! The correct answer was {random_decimal}."
                session['game_over'] = True  # Set game over to True
            else:
                result = f"Incorrect!. Please try again"
            session['counter'] += 1
            decimal_guess.loc[len(decimal_guess)] = [random_binary, random_decimal, user_guess, result]
            decimal_guess.to_csv('binary_to_decimal_results.csv', index=False)
        except ValueError:
            result = "Invalid input. Please enter a valid decimal number."   
    session['random_decimal'] = '{:08b}'.format(random_decimal)
    
    # Render template with the random binary and result message
    return render_template('binarytodecimal.html', 
                           random_binary=random_binary,
                           random_decimal=session.get('random_decimal'),
                           correct=correct, 
                           result=result, 
                           headers=headers, 
                           game_over=session['game_over'])
  
    
@app.route('/subnet-quiz', methods=['GET', 'POST'])
def subnet_quiz_route():
    
    if request.method == 'GET' or 'question' not in session or 'answer' not in session:
        # Generate a new question and answer
        question_data = generate_question_from_csv('questions.csv')
        
        # Store the question and answer in the session
        session['question'] = question_data['question']
        session['answer'] = question_data['answer']
        session['counter'] = 0
        session['game_over'] = False
        
    question = session.get('question')
    correct_answer = session.get('answer')
    
    result = None  # Default value for result
    correct = None
            
    if request.method == 'POST':
        user_answer = request.form['user_guess']
        try:
            # Check the user's answer
            if user_answer == correct_answer:
                result = f"Conragulations! You've guessed the correct answer of {correct_answer}" 
                session['game_over'] = True
            elif session['counter'] >= 2:
                result = f"Sorry, you've used all 3 tries! The correct answer was {correct_answer}."
                session['game_over'] = True  # Set game over to True
            else:
                result = f"Incorrect!. Please try again"
            session['counter'] += 1
        except ValueError:
            result = "Invalid input. Please enter a valid decimal number."

    # Render template with result and correct answer information
    return render_template('wildcardmask.html', result=result, correct=correct, question=question, game_over=session['game_over'])

if __name__ == '__main__':
    app.run(debug=True)


