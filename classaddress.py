"""
This file generates an classful address and calculates it based on certain questions
"""
import random
import ipaddress

def generate_random_classful_address():
    """
    Generate a random Class A, B, or C IP address with a subnet mask.
    
    Returns:
        tuple: 
            - ip (str): The randomly generated IP address.
            - default_mask (int): The default mask length for the IP's class.
            - cidr_prefix (int): A random CIDR prefix for subnetting.
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
        ip (str)
        default_mask (int)
        cidr_prefix (int)
      
    Returns:
        dict: 
            - Native Address Class: The IP's class (A, B, or C).
            - Native Address Map: Address range based on the default mask.
            - Subnet Address Map (SAM): Address range based on the CIDR prefix.
            - Subnet Mask (SNM): Subnet mask for the given CIDR prefix.
            - Wildcard Mask (WCM): Complement of the subnet mask.
    """
    # Convert the IP and CIDR prefix into a network object, to calculate laterrrr for subnet mask
    network = ipaddress.ip_network(f"{ip}/{cidr_prefix}", strict=False)

    # Calculates the native address range (using the default mask)
    native_network = ipaddress.ip_network(f"{ip}/{default_mask}", strict=False)
    native_address_map = f"{native_network.network_address} - {native_network.broadcast_address}"

    # Calculate the subnet range (using the CIDR prefix)
    subnet_address_map = f"{network.network_address} - {network.broadcast_address}"

    # Subnet Mask (SNM, (e.g., 255.255.255.0)) and Wildcard Mask (WCM)
    subnet_mask = str(network.netmask)
    wildcard_mask = str(network.hostmask)

    return {
        "Native Address Class": network.network_address.exploded.split(".")[0],
        "Native Address Map": native_address_map,
        "Subnet Address Map (SAM)": subnet_address_map,
        "Subnet Mask (SNM)": subnet_mask,
        "Wildcard Mask (WCM)": wildcard_mask
    }


