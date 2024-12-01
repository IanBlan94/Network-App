# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 17:20:32 2024

@author: isbla
"""
import unittest
from wildcard_mask import (
    calculate_wildcard_mask,
    prefix_length_to_subnet_mask,
    generate_ip_and_prefix,
    get_address_class_and_pattern,
    prefix_network_bits,
    prefix_host_bits
)

class TestWildcardMask(unittest.TestCase):

    def test_calculate_wildcard_mask(self):
        self.assertEqual(calculate_wildcard_mask(24), "0.0.0.255")
        self.assertEqual(calculate_wildcard_mask(16), "0.0.255.255")
        self.assertEqual(calculate_wildcard_mask(8), "0.255.255.255")

    def test_prefix_length_to_subnet_mask(self):
        self.assertEqual(prefix_length_to_subnet_mask(24), "255.255.255.0")
        self.assertEqual(prefix_length_to_subnet_mask(16), "255.255.0.0")
        self.assertEqual(prefix_length_to_subnet_mask(8), "255.0.0.0")

    def test_generate_ip_and_prefix(self):
        ip, prefix = generate_ip_and_prefix()
        self.assertTrue(1 <= int(ip.split(".")[0]) <= 223)
        self.assertTrue(1 <= prefix <= 32)

    def test_get_address_class_and_pattern(self):
        self.assertEqual(get_address_class_and_pattern("10.0.0.1"), ("A", "0"))
        self.assertEqual(get_address_class_and_pattern("172.16.0.1"), ("B", "10"))
        self.assertEqual(get_address_class_and_pattern("192.168.0.1"), ("C", "110"))
        self.assertEqual(get_address_class_and_pattern("240.0.0.1"), ("Unknown", "Unknown"))

    def test_prefix_network_bits(self):
        self.assertEqual(prefix_network_bits(24), "24")
        self.assertEqual(prefix_network_bits(16), "16")
        self.assertEqual(prefix_network_bits(8), "8")

    def test_prefix_host_bits(self):
        self.assertEqual(prefix_host_bits(24), "8")
        self.assertEqual(prefix_host_bits(16), "16")
        self.assertEqual(prefix_host_bits(8), "24")

if __name__ == "__main__":
    unittest.main()
