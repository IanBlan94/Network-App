from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
import random
import pandas as pd
from wildcard_mask import prefix_host_bits, prefix_length_to_subnet_mask, prefix_network_bits, get_address_class_and_pattern, load_questions_from_csv, subList, calculate_wildcard_mask
from classaddress import generate_random_classful_address, calculate_classful_analysis

headers = ["128", "64", "32", "16", "8", "4", "2", "1"]
decimal_guess = pd.DataFrame(columns=['Random Binary', 'Correct Decimal', 'User Guess', 'Result'])
binary_guess = pd.DataFrame(columns=['Random Decimal', 'Correct Binary', 'User Guess', 'Result'])
wildcardmak_results = pd.DataFrame(columns=['Random Question, Correct Answer', 'User Guess', 'Result'])
## NEEDS CSV FILE CREATION FOR CLASSFUL ADDRESS - AMY SANTJER ##

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
        session['wrong_guesses'] = []
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
                result = f"Congratulations! You've gotten it correct!" 
                session['game_over'] = True
                session['wrong_guesses'].clear
            else:
                session['wrong_guesses'].append(user_guess)  # Save wrong guess
                if session['counter'] >= 2:
                    result = f"Sorry, you've used all 3 tries! The correct answer was {random_binary}."
                    session['game_over'] = True  # Set game over to True
                    session['wrong_guesses'].clear
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
                           headers=headers, game_over=session['game_over'],
                           wrong_guesses=session.get('wrong_guesses', []))


@app.route("/binary-to-decimal", methods=['GET', 'POST'])
def binary_to_decimal():
        # Generate a new decimal-binary pair if the request is GET (page load)
    if request.method == 'GET' or 'random_decimal' not in session:
        random_decimal = random.randint(0, 255)
        random_binary = format(random_decimal, '08b')
        session['random_decimal'] = random_decimal  # Store decimal value in session
        session['counter'] = 0
        session['game_over'] = False
        session['wrong_guesses'] = []
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
                result = f"Congratulations! You've gotten it correct!" 
                session['game_over'] = True
                session['wrong_guesses'].clear
            else:
                session['wrong_guesses'].append(user_guess)
                if session['counter'] >= 2:
                    result = f"Sorry, you've used all 3 tries! The correct answer was {random_decimal}."
                    session['game_over'] = True  # Set game over to True
                    session['wrong_guesses'].clear
                else:
                    result = f"Incorrect!. Please try again"
            session['counter'] += 1
            
            decimal_guess.loc[len(decimal_guess)] = [random_binary, random_decimal, user_guess, result]
            decimal_guess.to_csv('binary_to_decimal_results.csv', index=False)
        except ValueError:
            result = "Invalid input. Please enter a valid decimal number."   
    
    
    # Render template with the random binary and result message
    return render_template('binarytodecimal.html', 
                           random_binary=random_binary,
                           random_decimal=session.get('random_decimal'),
                           correct=correct, 
                           result=result, 
                           headers=headers, 
                           game_over=session['game_over'],
                           wrong_guesses=session.get('wrong_guesses', []))
  
    
@app.route('/subnet-quiz', methods=['GET', 'POST'])
def subnet_quiz_route():
    # Load questions and generate answers
    
    if request.method == 'GET':
        session.pop('results', None)
        session.pop('questions_and_answers', None)
        questions_from_csv = load_questions_from_csv('questions.csv')
        questions_and_answers = []
        
        for question_data in questions_from_csv:
            ip, prefix_length = random.choice(subList)
            subnet_mask = prefix_length_to_subnet_mask(prefix_length)
            question = question_data["question"].replace("{ip}", ip).replace("{prefix_length}", str(prefix_length)).replace("{subnet_mask}", subnet_mask)

            # Dynamically generate correct answer
            if "Address Class" in question:
                correct_answer = f"{get_address_class_and_pattern(ip)[0]} / {get_address_class_and_pattern(ip)[1]}"
            elif "the prefix length" in question:
                correct_answer = str(prefix_length)
            elif "wildcard mask" in question:
                correct_answer = calculate_wildcard_mask(prefix_length)
            elif "the subnet mask" in question:
                correct_answer = prefix_length_to_subnet_mask(prefix_length)
            elif "network bits" in question:
                correct_answer = prefix_network_bits(prefix_length)
            elif "host bits" in question:
                correct_answer = prefix_host_bits(prefix_length)
            else:
                correct_answer = "Unknown"

            questions_and_answers.append({"question": question, "answer": correct_answer})

        # Store questions in the session
        session['questions_and_answers'] = questions_and_answers
        session['results'] = None

    elif request.method == 'POST':
        # Retrieve questions and submitted answers
        questions_and_answers = session.get('questions_and_answers', [])
        user_answers = request.form.to_dict()
        results = []

        for qa in questions_and_answers:
            user_answer = user_answers.get(qa["question"], "").strip()
            correct = user_answer == qa["answer"]
            results.append({
                "question": qa["question"],
                "correct_answer": qa["answer"],
                "user_answer": user_answer,
                "correct": correct
            })

        # Store results in session
        session['results'] = results

    return render_template('wildcardmask.html', questions=session.get('questions_and_answers', []), results=session.get('results'))


@app.route("/classful_quiz", methods=["GET", "POST"])
def classful_quiz():
    if request.method == "GET" or session.get("question") is None:
        ip, default_mask, cidr_prefix = generate_random_classful_address()
        answers = calculate_classful_analysis(ip, default_mask, cidr_prefix)

        question = f"Given the IP address {ip}/{cidr_prefix}, answer the following:"

        session["ip"] = ip
        session["cidr_prefix"] = cidr_prefix
        session["answers"] = answers
        session["question"] = question

        result = None  # No results yet for a new quiz
    else:
        user_answers = {
            key: request.form.get(key, "").strip() for key in session["answers"].keys()
        }
        correct_answers = session["answers"]

        # Validate user answers
        result = []
        for key, correct_answer in correct_answers.items():
            user_answer = user_answers.get(key, "")
            result.append({
                "question": key,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "correct": user_answer == correct_answer
            })

    return render_template("classfuladdress.html",
                           question=session["question"],
                           answers=session["answers"],
                           results=result)



if __name__ == '__main__':
    app.run(debug=True)


