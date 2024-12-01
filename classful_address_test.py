import unittest
from classaddress import (
    generate_random_classful_address,
    calculate_classful_analysis,
    validate_input
)

class TestClassAddress(unittest.TestCase):

    def test_generate_random_classful_address(self):
        ip, default_mask, cidr_prefix = generate_random_classful_address()
        self.assertTrue(1 <= int(ip.split(".")[0]) <= 223)
        self.assertTrue(default_mask in [8, 16, 24])
        self.assertTrue(default_mask + 1 <= cidr_prefix <= 30)

    def test_calculate_classful_analysis(self):
        ip = "192.168.1.0"
        default_mask = 24
        cidr_prefix = 28
        result = calculate_classful_analysis(ip, default_mask, cidr_prefix)
        self.assertEqual(result["Native Address Class"], "192")
        self.assertEqual(result["Leading Bit Pattern"], "110")
        self.assertEqual(result["Subnet Mask (SNM)"], "255.255.255.240")
        self.assertEqual(result["Wildcard Mask (WCM)"], "0.0.0.15")

    def test_validate_input(self):
        self.assertTrue(validate_input("Native Address Class", "192"))
        self.assertFalse(validate_input("Native Address Class", "300"))
        self.assertTrue(validate_input("Native Address Map", "192.H.H.H"))
        self.assertFalse(validate_input("Native Address Map", "192.H.300.H"))
        self.assertTrue(validate_input("Subnet Mask (SNM)", "255.255.255.0"))
        self.assertFalse(validate_input("Subnet Mask (SNM)", "300.255.255.0"))
        self.assertTrue(validate_input("Wildcard Mask (WCM)", "0.0.0.255"))
        self.assertFalse(validate_input("Wildcard Mask (WCM)", "300.0.0.255"))

if __name__ == "__main__":
    unittest.main()
