from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
import random
import pandas as pd
import webview
from wildcard_mask import calculate_subnet_address_map, prefix_host_bits, prefix_length_to_subnet_mask, prefix_network_bits, get_address_class_and_pattern, load_questions_from_csv, subList, calculate_wildcard_mask, generate_ip_and_prefix
from classaddress import generate_random_classful_address, calculate_classful_analysis, validate_input 


headers = ["128", "64", "32", "16", "8", "4", "2", "1"]
decimal_guess = pd.DataFrame(columns=['Random Binary', 'Correct Decimal', 'User Guess', 'Result'])
binary_guess = pd.DataFrame(columns=['Random Decimal', 'Correct Binary', 'User Guess', 'Result'])
wildcardmak_results = pd.DataFrame(columns=['Random Question, Correct Answer', 'User Guess', 'Result'])
classful_quiz_results = pd.DataFrame(columns=['IP Address', 'CIDR Prefix', 'Native Address Class', 'Native Address Map', 'Subnet Mask', 'Wildcard Mask', 'User Answers', 'Correct Answers', 'Score'])

app= Flask(__name__)
app.secret_key = 'theonekey'
webview.create_window("Networking Application",app)


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
                result = f"Congratulations! You got it right!" 
                session['game_over'] = True
                session['wrong_guesses'].clear
            else:
                session['wrong_guesses'].append(user_guess)  # Save wrong guess
                if session['counter'] >= 2:
                    result = f"Sorry, you've used all 3 tries! Correct answer: {random_binary}."
                    session['game_over'] = True  # Set game over to True
                    session['wrong_guesses'].clear
                else:
                    result = f"Good Effort! Please try again."
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
                result = f"Congratulations! You got it right!" 
                session['game_over'] = True
                session['wrong_guesses'].clear
            else:
                session['wrong_guesses'].append(user_guess)
                if session['counter'] >= 2:
                    result = f"Sorry, you've used all 3 tries! Correct answer: {random_decimal}."
                    session['game_over'] = True  # Set game over to True
                    session['wrong_guesses'].clear
                else:
                    result = f"Good Effort! Please try again."
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
    global wildcardmak_results  

    if request.method == 'GET' or session.get("question") is None:
        # Generate a random IP address and prefix
        ip, default_mask, prefix_length = generate_random_classful_address()
        subnet_mask = prefix_length_to_subnet_mask(prefix_length)
        answers = {
            "Subnet Address Map": calculate_subnet_address_map(ip, prefix_length),
            "Subnet Mask": subnet_mask,
            "Wildcard Mask": calculate_wildcard_mask(prefix_length)
        }

        question = f"Given the IP address {ip}/{prefix_length}, answer the following:"

        session["ip"] = ip
        session["prefix_length"] = prefix_length
        session["answers"] = answers
        session["question"] = question

        result = None
    else:
        # User submitted answers (POST request)
        user_answers = {
            key: request.form.get(key, "").strip() 
            for key in session["answers"].keys()
        }
        correct_answers = session["answers"]

        # Validate user answers and calculate results
        result = []
        score = 0
        
        for key, correct_answer in correct_answers.items():
            user_answer = user_answers.get(key, "").strip()
            
            # Normalize both answers for comparison
            normalized_user = user_answer.upper().replace(" ", "")
            normalized_correct = correct_answer.upper().replace(" ", "")
            
            # Compare normalized versions
            is_correct = normalized_user == normalized_correct
            
            if is_correct:
                score += 1
                
            result.append({
                "question": key,
                "user_answer": user_answer,
                "correct_answer": correct_answer if not is_correct else None,
                "correct": is_correct
            })

        # Log results
        wildcardmak_results.loc[len(wildcardmak_results)] = {
            'IP Address': session['ip'],
            'Prefix Length': session['prefix_length'],
            'Subnet Mask': correct_answers.get('Subnet Mask', ''),
            'Wildcard Mask': correct_answers.get('Wildcard Mask', ''),
            'User Answers': str(user_answers),
            'Correct Answers': str(correct_answers),
            'Score': f"{score}/{len(correct_answers)}"
        }

        wildcardmak_results.to_csv('subnet_quiz_results.csv', index=False)

    return render_template("wildcardmask.html",
                         question=session["question"],
                         answers=session["answers"],
                         results=result)

@app.route("/classful_quiz", methods=["GET", "POST"])
def classful_quiz():
    global classful_quiz_results  

    if request.method == "GET" or session.get("question") is None:
        ip, default_mask, cidr_prefix = generate_random_classful_address()
        answers = calculate_classful_analysis(ip, default_mask, cidr_prefix)

        question = f"Given the IP address {ip}/{cidr_prefix}, answer the following:"

        session["ip"] = ip
        session["cidr_prefix"] = cidr_prefix
        session["answers"] = answers
        session["question"] = question

        result = None  
    else:
        user_answers = {
            key: request.form.get(key, "").strip() for key in session["answers"].keys()
        }
        correct_answers = session["answers"]

        # Validate user answers
        result = []
        score = 0
        validation_error = False
        for key, correct_answer in correct_answers.items():
            user_answer = user_answers.get(key, "")
            # Check input validation
            if not validate_input(key, user_answer):
                validation_error = True
                result.append({
                    "question": key,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "correct": False,
                    "validation_error": True
                })
                continue
            is_correct = user_answer == correct_answer
            if is_correct:
                score += 1
            result.append({
                "question": key,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "correct": is_correct
            })
        
        # If there's a validation error, prevent quiz submission
        if validation_error:
            return render_template("classfuladdress.html",
                                   question=session["question"],
                                   answers=session["answers"],
                                   results=result,
                                   validation_error=True)

        # Log the results to the CSV
        classful_quiz_results.loc[len(classful_quiz_results)] = {
            'IP Address': session['ip'],
            'CIDR Prefix': session['cidr_prefix'],
            'Native Address Class': correct_answers.get('Native Address Class', ''),
            'Native Address Map': correct_answers.get('Native Address Map', ''),
            'Leading Bit Pattern': correct_answers.get('Leading Bit Pattern', ''),
            'Subnet Mask': correct_answers.get('Subnet Mask (SNM)', ''),
            'Wildcard Mask': correct_answers.get('Wildcard Mask (WCM)', ''),
            'User Answers': str(user_answers),
            'Correct Answers': str(correct_answers),
            'Score': f"{score}/{len(correct_answers)}"
        }

        # Save results to CSV after each quiz
        classful_quiz_results.to_csv('classful_quiz_results.csv', index=False)

    return render_template("classfuladdress.html",
                           question=session["question"],
                           answers=session["answers"],
                           results=result)
if __name__ == '__main__':
    #app.run(debug=True)
    webview.start()


