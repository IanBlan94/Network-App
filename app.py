from flask import Flask, flash, render_template, request, redirect, url_for, session 
import random
import pandas as pd
import os
#import webview
from wildcard_mask import calculate_subnet_address_map, prefix_host_bits, prefix_length_to_subnet_mask, prefix_network_bits, get_address_class_and_pattern, load_questions_from_csv, subList, calculate_wildcard_mask, generate_ip_and_prefix
from classaddress import generate_random_classful_address, calculate_classful_analysis, validate_input 
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

headers = ["128", "64", "32", "16", "8", "4", "2", "1"]
decimal_guess = pd.DataFrame(columns=['Random Binary', 'Correct Decimal', 'User Guess', 'Result'])
binary_guess = pd.DataFrame(columns=['Random Decimal', 'Correct Binary', 'User Guess', 'Result'])
wildcardmak_results = pd.DataFrame(columns=['Prefix Length', 'IP Address', 'User Name, Question', 'User Answer', 'Correct Answer', 'Result'])
classful_quiz_results = pd.DataFrame(columns=['IP Address', 'CIDR Prefix', 'Address Class', 'Native Address Map', 'Subnet Mask', 'Wildcard Mask', 'User Answers', 'Correct Answers', 'Score'])

app= Flask(__name__)
app.secret_key = 'theonekey'
#webview.create_window("Networking Application",app)

def init_db():
    """Initialize the database and create a 'users' & 'pets' table if it doesn't exist."""
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users
        (username TEXT PRIMARY KEY,
         password TEXT NOT NULL,
         profile_picture TEXT)
        ''')

@app.before_request
def before_first_request():
    """Run database initialization before the first request."""
    init_db()
    
@app.context_processor
def inject_user():
    """Inject the current logged-in username into all templates."""
    return dict(username=session.get('username'))

def get_user_details(username):
    """Retrieve user details from the database by username.
    Args:
        username (str): The username of the user.
    Returns:
        tuple: A tuple containing user details (username, bio, profile_picture, joined_date).
    """
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT username, profile_picture FROM users WHERE username = ?', (username,))
        return c.fetchone()
    


# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.
    GET: Render the login page.
    POST: Validate user credentials and log in the user.
    """
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Fetch user from the database
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('SELECT username, password FROM users WHERE username = ?', (username,))
            user = c.fetchone()
            
            # Validate password
            if user and check_password_hash(user[1], password):
                session['username'] = username
                return redirect(url_for('main'))
            message = 'Invalid username or password!'
        
    return render_template('login.html', message=message)

# Route for user logout
@app.route('/logout')
def logout():
    """Log out the user by clearing their session."""
    
    session.pop('username', None)
    return redirect(url_for('main'))

# Route for user registration
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """Handle user registration.
    GET: Render the registration page.
    POST: Create a new user account.
    """
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        try:
            # Insert new user into the database
            with sqlite3.connect('database.db') as conn:
                conn.execute(
                    'INSERT INTO users (username, password, profile_picture) VALUES (?, ?, ?)',
                    (username, password, None)
                )
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            message = 'Username Already Exists'
            
    return render_template('registration.html', message=message)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Assuming `username` is already in session or passed to the route
    username = session.get('username', None)
    user = get_user_details(session['username'])
    # Paths for each of the four CSV files
    file_paths = {
        "binary_to_decimal": f'user_data/{username}_binary_to_decimal_results.csv',
        "decimal_to_binary": f'user_data/{username}_decimal_to_binary_results.csv',
        "subnet_quiz": f'user_data/{username}_subnet_quiz_results.csv',
        "classful_quiz": f'user_data/{username}_classful_quiz_results.csv'
    }

    # Read data from each file and check if it's empty
    user_data = {}
    for key, path in file_paths.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            user_data[key] = {
                'data': df,
                'is_empty': df.empty
            }
        else:
            user_data[key] = {
                'data': None,
                'is_empty': True,
                'message': f"No results available for {key.replace('_', ' ').title()}."
            }

    # Pass the data and empty status to the template
    return render_template("profile.html", username=username, user_data=user_data, user=user)


@app.route('/')
def main():
    """Render the main page if logged in, otherwise render the login page."""
    
    if 'username' in session:
        user = get_user_details(session['username'])
        return render_template('main.html', user=user)
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

    # Default result for initial load
    result = None
    correct = None
    answer = None

    # Process the form submission (POST request)
    if request.method == 'POST':
        user_guess = request.form['user_guess']
        try:
            # Validate that the input is 8 bits of only 0 or 1
            if not all(bit in '01' for bit in user_guess) or len(user_guess) != 8:
                raise ValueError("Invalid binary input.")

            # Validate the guess
            if user_guess == random_binary:
                result = f"Congratulations! You got it right!" 
                correct = f"Correct Answer: {user_guess}"
                answer = "Correct"
                session['game_over'] = True
                session['wrong_guesses'].clear()
            else:
                session['wrong_guesses'].append(user_guess)  # Save wrong guess
                if session['counter'] >= 2:
                    result = f"Sorry, you've used all 3 tries! Correct answer: {random_binary}."
                    answer = f"Incorrect"
                    session['game_over'] = True  # Set game over to True
                    session['wrong_guesses'].clear()
                else:
                    result = f"Good Effort! Please try again."
                    answer = f"Incorrect"
            session['counter'] += 1

            # Save user result dynamically
            username = session.get('username', None)
            entry = {
                'Decimal': random_decimal,
                'Binary': random_binary,
                'Your Guess': user_guess,
                'Result': answer,
                'Correct': user_guess == random_binary
            }

            if username:
                os.makedirs('user_data', exist_ok=True)
                user_filename = os.path.join('user_data', f"{username}_decimal_to_binary_results.csv")

                if os.path.exists(user_filename):
                    df = pd.read_csv(user_filename)
                    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                else:
                    df = pd.DataFrame([entry])

                df['Result'] = df['Correct'].apply(lambda x: '✓ Correct!' if x else '✗ Incorrect')
                df.to_csv(user_filename, index=False)
            else:
                # Save in session temporarily
                if 'decimal_to_binary_results' not in session:
                    session['decimal_to_binary_results'] = []
                session['decimal_to_binary_results'].append(entry)

        except ValueError:
            result = "Invalid input. Please enter a valid 8-bit binary number."

    # For rendering
    headers = ["Decimal", "Binary", "Your Guess", "Result"]

    if 'username' in session:
        user = get_user_details(session['username'])
        return render_template('decimaltobinary.html',
                                user=user,
                                random_decimal=random_decimal,
                                random_binary=session.get('random_binary'),
                                result=result,
                                correct=correct,
                                headers=headers,
                                game_over=session['game_over'],
                                wrong_guesses=session.get('wrong_guesses', []))
    else:
        return render_template('decimaltobinary.html',
                                random_decimal=random_decimal,
                                random_binary=session.get('random_binary'),
                                result=result,
                                correct=correct,
                                headers=headers,
                                game_over=session['game_over'],
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
        random_decimal = session.get('random_decimal')
        random_binary = format(random_decimal, '08b')

    result = None
    correct = None

    # Retrieve the values from the session for POST (submission)
    if request.method == 'POST':
        user_guess = request.form['user_guess']
        try:
            user_guess = int(user_guess)

            if user_guess == random_decimal:
                result = f"Congratulations! You got it right!"
                correct = f"Correct Answer: {user_guess}"
                session['game_over'] = True
                session['wrong_guesses'].clear()
                answer = f"Correct"
            else:
                session['wrong_guesses'].append(user_guess)
                if session['counter'] >= 2:
                    result = f"Sorry, you've used all 3 tries! Correct answer: {random_decimal}."
                    session['game_over'] = True
                    session['wrong_guesses'].clear()
                    answer = f"Incorrect"
                else:
                    result = f"Good Effort! Please try again."
                    answer = f"Incorrect"
            session['counter'] += 1

            # Save user result dynamically
            username = session.get('username', None)
            entry = {
                'Binary': random_binary,
                'Decimal': random_decimal,
                'Your Guess': user_guess,
                'Result': answer,
                'Correct': user_guess == random_decimal
            }


            if username:
                os.makedirs('user_data', exist_ok=True)
                user_filename = os.path.join('user_data', f"{username}_binary_to_decimal_results.csv")

                if os.path.exists(user_filename):
                    df = pd.read_csv(user_filename)
                    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                else:
                    df = pd.DataFrame([entry])
                
                df['Result'] = df['Correct'].apply(lambda x: '✓ Correct!' if x else '✗ Incorrect')
                df.to_csv(user_filename, index=False)
            else:
                # Save in session temporarily
                if 'binary_to_decimal_results' not in session:
                    session['binary_to_decimal_results'] = []
                session['binary_to_decimal_results'].append(entry)

        except ValueError:
            result = "Invalid input. Please enter a valid decimal number."

    # For rendering
    headers = ["Binary", "Decimal", "Your Guess", "Result"]

    if 'username' in session:
        user = get_user_details(session['username'])
        return render_template('binarytodecimal.html',
                                user=user,
                                random_binary=random_binary,
                                random_decimal=session.get('random_decimal'),
                                correct=correct,
                                result=result,
                                headers=headers,
                                game_over=session['game_over'],
                                wrong_guesses=session.get('wrong_guesses', []))
    else:
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

        # Save into session for next POST
        session["ip"] = ip
        session["prefix_length"] = prefix_length
        session["answers"] = answers
        session["question"] = question

        result = None

    else:
        # POST request: user submitted answers
        user_answers = {
            key: request.form.get(key, "").strip()
            for key in session["answers"].keys()
        }
        correct_answers = session["answers"]

        result = []
        score = 0
        username = session.get('username', None)

        for key, correct_answer in correct_answers.items():
            user_answer = user_answers.get(key, "").strip()

            normalized_user = user_answer.upper().replace(" ", "")
            normalized_correct = correct_answer.upper().replace(" ", "")

            is_correct = normalized_user == normalized_correct
            if is_correct:
                score += 1

            result.append({
                'IP Address': session['ip'],
                'Prefix Length': session['prefix_length'],
                "question": key,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "correct": is_correct
            })

        # Print for debugging
        print("Results to be saved:")
        for res in result:
            print(f"Question: {res['question']}, User Answer: {res['user_answer']}, Correct Answer: {res['correct_answer']}, Result: {'✓ Correct!' if res['correct'] else '✗ Incorrect'}")

        # Turn result into DataFrame
        result_df = pd.DataFrame(result)
        result_df['Result'] = result_df['correct'].apply(lambda x: '✓ Correct!' if x else '✗ Incorrect')

        # Save based on login status
        if username:
            # Make sure the user_data folder exists
            os.makedirs('user_data', exist_ok=True)

            user_filename = os.path.join('user_data', f"{username}_subnet_quiz_results.csv")
            
            if os.path.exists(user_filename):
                existing_df = pd.read_csv(user_filename)
                updated_df = pd.concat([existing_df, result_df], ignore_index=True)
            else:
                updated_df = result_df

            updated_df.to_csv(user_filename, index=False)
        
        else:
            # Save temporary results in session for guests
            session['quiz_results'] = result

    # Prepare data to show the quiz page
    if 'username' in session:
        user = get_user_details(session['username'])
        return render_template("wildcardmask.html",
                                user=user,
                                question=session["question"],
                                answers=session["answers"],
                                results=result)
    else:
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

        result = []
        score = 0
        username = session.get('username', None)

        validation_error = False
        for key, correct_answer in correct_answers.items():
            user_answer = user_answers.get(key, "")

            is_correct = user_answer == correct_answer
            if is_correct:
                score += 1

            result.append({
                "IP Address": session["ip"],
                "CIDR Prefix": session["cidr_prefix"],
                "question": key,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "correct": is_correct
            })

        if validation_error:
            return render_template("classfuladdress.html",
                                   question=session["question"],
                                   answers=session["answers"],
                                   results=result,
                                   validation_error=True)

        # --- Save to file or session because NO validation errors ---
        result_df = pd.DataFrame(result)
        result_df['Result'] = result_df['correct'].apply(lambda x: '✓ Correct!' if x else '✗ Incorrect')

        if username:
            os.makedirs('user_data', exist_ok=True)
            user_filename = os.path.join('user_data', f"{username}_classful_quiz_results.csv")

            if os.path.exists(user_filename):
                existing_df = pd.read_csv(user_filename)
                updated_df = pd.concat([existing_df, result_df], ignore_index=True)
            else:
                updated_df = result_df

            updated_df.to_csv(user_filename, index=False)
        else:
            session['classful_quiz_results'] = result

    # --- Final rendering ---
    if 'username' in session:
        user = get_user_details(session['username'])
        return render_template("classfuladdress.html",
                               user=user,
                               question=session["question"],
                               answers=session["answers"],
                               results=result)
    else:
        return render_template("classfuladdress.html",
                               question=session["question"],
                               answers=session["answers"],
                               results=result)

@app.route('/delete_results/<quiz_type>', methods=['POST'])
def delete_results(quiz_type):
    username = session.get('username')
   
    # Map quiz_type to filename suffix
    filename_suffixes = {
        'binary_to_decimal': '_binary_to_decimal_results.csv',
        'decimal_to_binary': '_decimal_to_binary_results.csv',
        'subnet_quiz': '_subnet_quiz_results.csv',
        'classful_quiz': '_classful_quiz_results.csv'
    }

    suffix = filename_suffixes.get(quiz_type)
    if not suffix:
        flash("Invalid quiz type.")
        return redirect(url_for('profile'))

    user_filename = os.path.join('user_data', f"{username}{suffix}")

    if os.path.exists(user_filename):
        os.remove(user_filename)
        flash(f"{quiz_type.replace('_', ' ').title()} results deleted.")
    else:
        flash("File not found.")

    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True)
    #webview.start()


