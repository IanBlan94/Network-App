# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 17:20:32 2024

@author: isbla
"""
import unittest
from wildcard_mask import (
    prefix_length_to_subnet_mask,
    prefix_network_bits,
    prefix_host_bits,
    calculate_wildcard_mask,
    get_address_class_and_pattern,
    load_questions_from_csv,
    generate_question_from_csv
)

class TestSubnetQuizFunctions(unittest.TestCase):
    
    def test_prefix_length_to_subnet_mask(self):
        # Test for known prefix lengths and expected subnet masks
        self.assertEqual(prefix_length_to_subnet_mask(24), "255.255.255.0")
        self.assertEqual(prefix_length_to_subnet_mask(16), "255.255.0.0")
        self.assertEqual(prefix_length_to_subnet_mask(8), "255.0.0.0")

    def test_prefix_network_bits(self):
        # Test network bits from prefix length
        self.assertEqual(prefix_network_bits(24), "24")
        self.assertEqual(prefix_network_bits(16), "16")
        self.assertEqual(prefix_network_bits(8), "8")

    def test_prefix_host_bits(self):
        # Test host bits calculation from prefix length
        self.assertEqual(prefix_host_bits(24), "8")  # 32 - 24 = 8
        self.assertEqual(prefix_host_bits(16), "16")  # 32 - 16 = 16
        self.assertEqual(prefix_host_bits(8), "24")   # 32 - 8 = 24

    def test_calculate_wildcard_mask(self):
        # Test wildcard mask calculation for various prefix lengths
        self.assertEqual(calculate_wildcard_mask(24), "0.0.0.255")
        self.assertEqual(calculate_wildcard_mask(16), "0.0.255.255")
        self.assertEqual(calculate_wildcard_mask(8), "0.255.255.255")

    def test_get_address_class_and_pattern(self):
        # Test address class and pattern determination
        self.assertEqual(get_address_class_and_pattern("10.0.0.0"), ('A', '0'))
        self.assertEqual(get_address_class_and_pattern("172.16.0.0"), ('B', '10'))
        self.assertEqual(get_address_class_and_pattern("192.168.1.1"), ('C', '110'))
        self.assertEqual(get_address_class_and_pattern("224.0.0.1"), ('Unknown', 'Unknown'))

    def test_load_questions_from_csv(self):
        # This test assumes a test CSV file named 'test_questions.csv' exists with sample questions.
        questions = load_questions_from_csv('questions.csv')
        self.assertTrue(isinstance(questions, list))
        self.assertTrue(len(questions) > 0)
        self.assertIn("question", questions[0])

    def test_generate_question_from_csv(self):
        # Test question generation logic
        question_data = generate_question_from_csv('questions.csv')
        self.assertIn("question", question_data)
        self.assertIn("answer", question_data)
        self.assertIn("ip", question_data)
        self.assertIn("prefix_length", question_data)

if __name__ == '__main__':
    unittest.main()
