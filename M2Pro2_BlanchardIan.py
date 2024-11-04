# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 09:38:05 2024

@author: isbla
"""

#Binary-Decimal Conversion Game

import random
import pandas as pd # type: ignore
from wildcard_mask import subnet_quiz   

# Initialize DataFrames to store guesses
decimal_guess = pd.DataFrame(columns=['Random Binary', 'Correct Decimal', 'User Guess', 'Result'])
binary_guess = pd.DataFrame(columns=['Random Decimal', 'Correct Binary', 'User Guess', 'Result'])

def display_bit_representation(binary_str):
    headers = ["128", "64", "32", "16", "8", "4", "2", "1"]
    binary_values = list(binary_str)

    # Print the headers with spacing
    header_row = " | ".join(f"{header:<3}" for header in headers)
    print(header_row)
    print("-" * len(header_row))

    # Print the binary values aligned with headers and spaced
    value_row = " | ".join(f"{value:<3}" for value in binary_values)
    print(value_row)
    return headers, binary_values

def binary_to_decimal():
    while True:
        # Generate a random decimal number between 0 and 255
        random_decimal = random.randint(0, 255)
        # Convert the decimal number to its 8-bit binary equivalent
        random_binary = format(random_decimal, '08b')
        
        #Displays a binary table to reference 
        print("\nBit representation:")
        display_bit_representation(f"{random_binary}")
        
        print(f"\nRandom binary number: {random_binary}")
        user_guess = input("Enter the decimal value for this binary number: ")
        
        # Handles user input and exception handling
        try:
            user_guess = int(user_guess)
            if user_guess == random_decimal:
                print("Congratulations! You guessed correctly.")
                result = "Correct"
            else:
                print(f"Sorry, that's incorrect. The correct decimal value is {random_decimal}.")
                result = "Wrong"
            
            print("\nBit representation of the binary number:")
            display_bit_representation(random_binary)
            
            # Save to DataFrame
            decimal_guess.loc[len(decimal_guess)] = [random_binary, random_decimal, user_guess, result]
            
            choice = input("\n1) Reset (generate another random binary)\n2) Back to main menu\nEnter your choice: ")
            if choice == '2':
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

def decimal_to_binary():
    while True:
        # Generate a random decimal number between 0 and 255
        random_decimal = random.randint(0, 255)
        
        # Convert the decimal number to its 8-bit binary equivalent
        correct_binary = format(random_decimal, '08b')
        
        #Displays a binary table to reference 
        print("\nBit representation:")
        display_bit_representation("00000000")
        
    
        print(f"\nRandom decimal number: {random_decimal}")
        
        
        # Handles user input and exception handling
        try:
            user_guess = input("Enter the binary value for this number: ")
            if user_guess == correct_binary:
                print("Congratulations! You guessed correctly.")
                result = "Correct"
            else:
                print(f"Sorry, that's incorrect. The correct  value is {correct_binary}.")
                result = "Wrong"
            
            print("\nBit representation of the binary number:")
            display_bit_representation(correct_binary)
            
            # Save to DataFrame
            decimal_guess.loc[len(decimal_guess)] = [correct_binary, random_decimal, user_guess, result]
            
            choice = input("\n1) Reset (generate another random binary)\n2) Back to main menu\nEnter your choice: ")
            if choice == '2':
                break
        except ValueError:
            print("Invalid input. Please enter a number.")



def main_menu():
    #Displays a menu to choose from
    while True:
        print("\nMain Menu:")
        print("1. Binary to Decimal Conversion")
        print("2. Decimal to Binary Conversion")
        print("4 Subnet Mask Practice")
        print("9. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            binary_to_decimal()
        elif choice == '2':
            decimal_to_binary()
        elif choice == '4':
            subnet_quiz()
        elif choice == '9':
            print("Thank you for using the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
    
    # Save DataFrames to CSV files
    decimal_guess.to_csv('decimal_guess.csv', index=False)
    binary_guess.to_csv('binary_guess.csv', index=False)

if __name__ == "__main__":
    main_menu()