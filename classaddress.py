"""
This file generates an classful address and calculates it based on certain questions

@author: amyxg
"""
import random
import ipaddress
import re

def generate_random_classful_address():
    """
    Generate a random Class A, B, or C IP address with a subnet mask.
    
    Returns:
        tuple: 
            - ip (str): The randomly generated IP address.
            - default_mask (int): The default mask length for the IP's class.
            - cidr_prefix (int): A random CIDR prefix for subnetting.
    
     Doctests:
        >>> ip, mask, prefix = generate_random_classful_address()
        >>> isinstance(ip, str)
        True
        >>> isinstance(mask, int)
        True
        >>> isinstance(prefix, int)
        True
    """
    # chooses random str of A, B, or C
    address_class = random.choice(['A', 'B', 'C'])
    
    if address_class == 'A': # A = range of 1.0.0.0 to 126.255.255.255
        ip = f"{random.randint(1, 126)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        default_mask = 8
    elif address_class == 'B': # B = range of 128.0.0.0 to 191.255.255.255
        ip = f"{random.randint(128, 191)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        default_mask = 16
    else:  # C = range of 192.0.0.0 to 223.255.255.255
        ip = f"{random.randint(192, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        default_mask = 24

    #  used for subnetting, cidr_prefix is a number between the default mask (e.g., /8, /16, /24) and /30.
    cidr_prefix = random.randint(default_mask + 1, 30)
    return ip, default_mask, cidr_prefix


def calculate_classful_analysis(ip, default_mask, cidr_prefix):
    """
    Calculate details for the given IP, default mask, and CIDR prefix.

    Args:
        ip (str): IP address
        default_mask (int): Default mask length for the IP's class
        cidr_prefix (int): CIDR prefix for subnetting
      
    Returns:
        dict: 
            - Address Class: The IP's class (A, B, or C)
            - Native Address Map: Address range based on the default mask
            - Subnet Mask (SNM): Subnet mask for the given CIDR prefix
            - Wildcard Mask (WCM): Complement of the subnet mask

    Doctests:
        >>> result = calculate_classful_analysis('10.0.0.1', 8, 24)
        >>> result['Address Class']
        'A'
        >>> result['Native Address Map']
        '10.H.H.H'
    """
    # Convert the IP and CIDR prefix into a network object
    network = ipaddress.ip_network(f"{ip}/{cidr_prefix}", strict=False)

    # Split the IP into octets
    octets = ip.split('.')

    # Determine address class and native address map
    first_octet = int(octets[0])
    if 1 <= first_octet <= 126:  # Class A
        leading_bit_pattern = "0"
        native_address_map = f"{first_octet}.H.H.H"
        address_class = "A"
    elif 128 <= first_octet <= 191:  # Class B
        leading_bit_pattern = "10"
        native_address_map = f"{first_octet}.{octets[1]}.H.H"
        address_class = "B"
    elif 192 <= first_octet <= 223:  # Class C
        leading_bit_pattern = "110"
        native_address_map = f"{first_octet}.{octets[1]}.{octets[2]}.H"
        address_class = "C"
    else:
        leading_bit_pattern = "Unknown"
        native_address_map = "Invalid Address Class"
        address_class = "Invalid"

    return {
        "Address Class": address_class,
        "Leading Bit Pattern": leading_bit_pattern,
        "Native Address Map": native_address_map,
        "Subnet Mask (SNM)": str(network.netmask),
        "Wildcard Mask (WCM)": str(network.hostmask)
    }

def validate_input(key, value):
    """
    Validate user input based on the question type

    Args:
        key:
        value:

    Returns:
        bool: False

     Doctests:
        >>> validate_input('Address Class', 'A')
        True
        >>> validate_input('Address Class', 'F')
        False
        >>> validate_input('Native Address Map', '10.H.H.H')
        True
        >>> validate_input('Leading Bit Pattern', '0')
        True
        >>> validate_input('Subnet Mask (SNM)', '255.255.255.0')
        True
        >>> validate_input('Wildcard Mask (WCM)', '0.0.0.255')
        True
    """
    if key == "Address Class":
        # Must be one of A, B, C, D, or E (case-insensitive)
        return value.upper() in ['A', 'B', 'C', 'D', 'E']
    
    # Rest of the validation function remains the same
    elif key == "Native Address Map":
        return re.match(r'^\d+\.\d*[H]+\.\d*[H]+\.\d*[H]+$', value) is not None
    
    elif key == "Leading Bit Pattern":
        # Must be a binary string
        return all(bit in '01' for bit in value)
    
    elif key == "Subnet Mask (SNM)":
        try:
            octets = list(map(int, value.split(".")))
            if len(octets) != 4 or not all(0 <= octet <= 255 for octet in octets):
                return False
            mask_binary = "".join(f"{octet:08b}" for octet in octets)
            return re.match(r"^1*0*$", mask_binary) is not None
        except ValueError:
            return False
    
    elif key == "Wildcard Mask (WCM)":
        try:
            octets = list(map(int, value.split(".")))
            if len(octets) != 4 or not all(0 <= octet <= 255 for octet in octets):
                return False
            mask_binary = "".join(f"{octet:08b}" for octet in octets)
            return re.match(r"^0*1*$", mask_binary) is not None
        except ValueError:
            return False
            
    return False

if __name__ == "__main__":
    import doctest
    doctest.testmod()