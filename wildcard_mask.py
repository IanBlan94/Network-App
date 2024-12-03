# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 22:39:19 2024

@author: isbla
"""

import random
import csv

# Define the list of subnets with their associated prefix lengths
subList = [
    ("10.0.0.0", 8),
    ("172.16.0.0", 12),
    ("192.168.1.0", 24),
    ("192.0.2.0", 24),
    ("203.0.113.0", 24),
    ("198.51.100.0", 24),
    ("172.20.0.0", 16),
    ("10.10.10.0", 24),
    ("192.168.100.0", 24),
    ("172.31.255.0", 16),
    ("17.127.170.14", 11),
    ("123.53.14.25", 15),
    ("79.123.14.110", 14),
    ("131.47.236.246", 24),
    ("111.97.204.185", 21),
    ("114.243.35.164", 28),
    ("20.145.123.103", 17),
    ("46.2.38.35", 8),
    ("28.203.125.76", 14),
    ("49.49.218.206", 21)
]

def generate_ip_and_prefix():
    """
    Generate a random valid Class A, B, or C IP address with a valid prefix length.
    
    Returns:
        tuple: A tuple containing a valid IP (str) and prefix length (int).
    """
    while True:
        # Generate a random IP
        first_octet = random.choice(range(1, 224))  # Class A, B, or C
        ip = f"{first_octet}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        
        # Generate a valid prefix length
        prefix_length = random.randint(1, 32)
        
        return ip, prefix_length

def calculate_subnet_address_map(ip, prefix_length):
    """
    Calculate the Subnet Address Map (SAM) for a given IP and prefix length.

    Args:
        ip (str): The IP address.
        prefix_length (int): The prefix length.

    Returns:
        str: SAM with N/S/H bits per octet (e.g., "N.N.S.H")

    Example:
        >>> calculate_subnet_address_map("192.168.1.0", 24)
        "N.N.N.H"
    """
    # Convert prefix length to a total of 32 bits
    sam_bits = []
    
    # Fill in network bits (N)
    for i in range(prefix_length):
        sam_bits.append('N')
    
    # Fill in host bits (H)
    for i in range(32 - prefix_length):
        sam_bits.append('H')
    
    # Convert bits to octets (groups of 8)
    sam_octets = []
    for i in range(0, 32, 8):
        octet = ''.join(sam_bits[i:i+8])
        sam_octets.append(octet)
    
    # Join octets with dots
    return '.'.join(sam_octets)

def prefix_length_to_subnet_mask(prefix_length):   
    """
  Convert a prefix length into a subnet mask.

  Args:
      prefix_length (int): The length of the prefix, indicating the number of
      bits used for the network portion of the address.
      
  Returns:
      str: The subnet mask in dotted decimal format. (ex. 255.255.255.0)
  """
    
    mask = (0xFFFFFFFF >> (32 - prefix_length)) << (32 - prefix_length)
    octets = [(mask >> (24 - i * 8)) & 0xFF for i in range(4)]
    return '.'.join(str(octet) for octet in octets)

# determines buts for subnet mask. Question 5


def prefix_network_bits(prefix_length):
    
    """
  Determine the number of network bits from a given prefix length.

  Args:
      prefix_length (int): The length of the prefix.

  Returns:
      str: The number of network bits as a string.
  """
    
    # The number of network bits is simply the prefix length
    network_bits = prefix_length
    
    # Return only the network bits
    return str(network_bits)

def prefix_host_bits(prefix_length):
    
    """
    Determine the number of host bits from a given prefix length.

    Args:
        prefix_length (int): The length of the prefix.

    Returns:
        str: The number of host bits as a string.
    """
    
    # The number of network bits is simply the prefix length
    network_bits = prefix_length
    host_bits = 32 - network_bits
    # Return only the network bits
    return str(host_bits)


# Function to calculate wildcard mask as inverse of the subnet mask
def calculate_wildcard_mask(prefix_length):
    
    """
   Calculate the wildcard mask, which is the inverse of the subnet mask.

   Args:
       prefix_length (int): The length of the prefix.

   Returns:
       str: The wildcard mask in dotted decimal format. (ex. "0.0.0.255")
   """
    
    subnet_mask = prefix_length_to_subnet_mask(prefix_length)
    return '.'.join(str(255 - int(octet)) for octet in subnet_mask.split('.'))

# Function to determine the class and pattern of an IP address


def get_address_class_and_pattern(ip):
    
    """
  Determine the class and leading pattern of an IP address.

  Args:
      ip (str): The IP address in dotted decimal format.

  Returns:
      tuple: A tuple containing the class ('A', 'B', 'C', or 'Unknown') 
      and the pattern ('0', '10', '110', or 'Unknown').
  """
    
    first_octet = int(ip.split('.')[0])
    if 1 <= first_octet <= 126:
        return 'A', '0'
    if 128 <= first_octet <= 191:
        return 'B', '10'
    if 192 <= first_octet <= 223:
        return 'C', '110'
    else:
        return 'Unknown', 'Unknown'

# Load questions from the CSV file (only the question text)


def load_questions_from_csv(filename):
    
    """
   Load questions and their answers from a CSV file.

   Args:
       filename (str): The path to the CSV file containing the questions.

   Returns:
       list: A list of dictionaries, each containing 'question' and 'answer' keys.
   """
    
    questions = []
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            question = row[0]
            questions.append({"question": question})
    return questions

# Generate a random subnet and pick a question from the CSV


def generate_question_from_csv(filename):
     
    """
    Randomly select a question from a CSV file.


    Args:
        filename (str): The path to the CSV file containing the questions.

    Returns:
        dict: A dictionary containing 'question' and 'answer' keys.
    """
    # Load the questions from the CSV file
    questions = load_questions_from_csv(filename)

    # Pick a random subnet and prefix length from subList
    ip, prefix_length = random.choice(subList)

    # Pick a random question from the loaded questions
    selected_question = random.choice(questions)

    sub_func = prefix_length_to_subnet_mask(prefix_length)

    # Replace placeholders with the correct output
    question_with_subnet = selected_question["question"].replace("{ip}", ip).replace("{prefix_length}",
                                            str(prefix_length)).replace("{subnet_mask}", sub_func)

    # Dynamically generate the correct answer
    if "Address Class" in question_with_subnet:
        correct_answer=f"{get_address_class_and_pattern(ip)[0]} / " \
                 f"{get_address_class_and_pattern(ip)[1]}"
    elif "the prefix length" in question_with_subnet:
        correct_answer=str(prefix_length)
    elif "wildcard mask" in question_with_subnet:
        correct_answer=calculate_wildcard_mask(prefix_length)
    elif "the subnet mask" in question_with_subnet:
        correct_answer=prefix_length_to_subnet_mask(prefix_length)
    elif "network bits" in question_with_subnet:
        # Get network and host bits using the prefix_bits function
        correct_answer=prefix_network_bits(prefix_length)
    elif "host bits" in question_with_subnet:
        # Get network and host bits using the prefix_bits function
        correct_answer=prefix_host_bits(prefix_length)
    else:
        correct_answer="Unknown"

    return {"question": question_with_subnet, "answer": correct_answer,
            "ip": ip, "prefix_length": prefix_length}

# Ask the question and check the user's answer
def ask_question(question_data):
    
    """
    Ask a question to the user and check their answer.

    Args:
        question_data (dict): A dictionary containing 'question' and 'answer' keys.

    Returns:
        bool: True if the user answers correctly, False otherwise.
    """
    
    counter=0
    while counter < 3:
        print(question_data['question'])
        user_answer=input("Your answer: ").strip()

        # Normalize both user answer and correct answer
        normalized_user_answer=user_answer.lower().replace(
            " / ", "/").replace(" /", "/").replace("/ ", "/").strip()
        normalized_correct_answer=question_data['answer'].lower().replace(
            " / ", "/").replace(" /", "/").replace("/ ", "/").strip()

        # Compare the normalized versions
        is_correct=normalized_user_answer == normalized_correct_answer

        if is_correct:
            print("Congratulations! Your answer is correct.")
            counter=3
        else:
            print("Sorry, that's incorrect. Please try again\n")
            counter += 1
    if not is_correct:
        print(
            f"Sorry you did not guess correctly. The correct answer is: {question_data['answer']}")
    # Save the result to a CSV file
    save_result('wildcard.csv', question_data['question'], question_data['answer'],
                user_answer, "Correct" if is_correct else "Incorrect")

    return is_correct

# Save the result of each question attempt
def save_result(filename, question, correct_answer, user_answer, result):
    
    """
    Save the result of a quiz question to a CSV file.

    Args:
        filename (str): The path to the CSV file.
        question (str): The quiz question.
        correct_answer (str): The correct answer.
        user_answer (str): The user's answer.
        result (str): "Correct" or "Incorrect", indicating whether the user's answer was correct.
    """
    
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer=csv.writer(file)
        writer.writerow([question, correct_answer, user_answer, result])

# Run the subnet quiz
def subnet_quiz():
    
    """
    Run the subnet quiz by loading and asking questions from the CSV file.

    Offers the user the choice to reset or return to the main menu after each question.
    """
    
    while True:
        # Load and ask questions from the CSV
        question_data=generate_question_from_csv('questions.csv')
        ask_question(question_data)

        # Offer a choice to ask another question or go back to the main menu
        choice=input(
            "Enter 'r' to reset (ask another question) or 'm' to return to main menu: ").lower()
        if choice == 'm':
            break


