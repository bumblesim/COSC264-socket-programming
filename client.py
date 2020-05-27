import socket
import sys
import os.path
from time import strftime

"""
client.py
COSC264 Socket Assignment
Author: Simon Lorimer
ID: 34339189
"""

def getinfo():
    """ Requests an input from the user to specify an IP address (or hostname),
    Port number and file name. Checks to make sure there are not more than three
    entries. Returns the three values needed. """
    #Gather the three inputs
    three_inputs = input("Please enter in an IP address, Port number and file name seperated by a space: ").split()
    if ((len(three_inputs) < 3) or (len(three_inputs) > 3)):
        sys.exit("Invalid entry.\nThe program will now exit.")
    return three_inputs[0], three_inputs[1], three_inputs[2]

def validate_ip(ip_addr):
    """ Validates the IP address by calling gethostbyname(), which will convert
    a server host (if entered) to an IP address. If it is not a valid IP, the
    program will exit will an error."""
    try:
        ip_addr = socket.gethostbyname(ip_addr)
    except socket.error:
        sys.exit("Invalid IP address.\nThe program will now exit.")
    return ip_addr

def validate_port(port_num):
    """ Validates the Port number by trying to convert the String to an Integer.
    If this fails, the program will exit with an error. The function will also
    ensure that the port number is beetween the values if 1024 - 64000
    (including). """ 
    try:  
        port_num = int(port_num)
    except:
        sys.exit("Invalid Port.\nThe program will now exit.")
    
    if ((int(port_num) < 1024) or (int(port_num) > 64000)):
        sys.exit(port_num + " is an incorrect port value.\nThe program will now exit.") 
    return port_num

def validate_file(file_name):
    """Checks the the file input is valid. If not, the program will exit. If
    the file is found, it will return. """
    if os.path.isfile(file_name) is False:
        sys.exit("Unable to locate file.\nThe program will now exit.")
    return

def create_connect_socket(ip_addr, port_num):
    """ Attempts to create a socket and connect to the given IP address and
    port number. If unsuccessful, the program will exit with information. """
    try:   
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        sys.exit("Unable to create socket.\nThe program will now exit.")
    s.settimeout(1)
    try:
        s.connect((ip_addr, port_num))
    except:
        sys.exit("Unable to connect.\nThe program will now exit.") 
    return s

def connection_msg(s):
    """ Waits to receive the initial connection message. Will return once this 
    has been recevied. """
    bool_msg = True
    while bool_msg:
        msg = s.recv(200)
        print(str(msg, 'utf-8'))
        bool_msg = False
        return
    
def create_filerequest(file_name):
    """ Creates a bytearray for filerequest packet. Checks to make sure the 
    length of the file is fine otherwise will exit. Returns a bytearray in the 
    format of file request. """
    file_request = bytearray()
    
    magic_num = 0x497E
    pkt_type = 1
    file_len = len(file_name)
    if file_len < 1 or file_len > 1024:
        sys.exit("Invalid file length.\nThe program will now exit.")
    
    file_request.extend(magic_num.to_bytes(2, byteorder = "big"))
    file_request.extend(pkt_type.to_bytes(1, byteorder = "big"))
    file_request.extend(file_len.to_bytes(2, byteorder = "big"))
    
    ascii_file = [ord(c) for c in file_name]
    
    for each in ascii_file:
        file_request.extend(int(each).to_bytes(1, byteorder = "big"))
    return file_request

def receive_fileresponse(s):
    """ Receives the file response and will perform checks to ensure that the
    data is valid. If it isn't the program will exit with the appropriate error.
    """
    magic_one = str(hex(s.recv(1)[0])) + str(hex(s.recv(1)[0]))[-2:]
    magic_int_num = int(magic_one, 16)
    magic_num = hex(magic_int_num)
    if magic_int_num != 18814:
        s.close()
        sys.exit("Invalid Magic number.\nThe program will now exit.")
    
    pkt_type = int(s.recv(1)[0])
    if pkt_type != 2:
        s.close()
        sys.exit("Invalid Packet type.\nThe program will now exit.")
    
    status_code = int(s.recv(1)[0])
    if status_code != 1:
        data_len = 0
        s.close()
        sys.exit("No data on incoming packet.\nThe program will now exit.")
    
    data_len = int.from_bytes(s.recv(4), byteorder = "big", signed = False)
    data_text = str(s.recv(data_len), 'utf-8')
    return data_text

def write_to_file(file_name, data_text):
    """ Writes a string from data_text to the file_name. Returns once complete. 
    """
    file = open(file_name, "w")
    file.write(data_text)
    file.close()
    print(f"File {file_name} has successfully been received written to {file_name}")
    return

def main():
    """ Main function of the program. Mostly calls other functions and acts as
    a fully functional client. Asks the user to input an IP address, port number
    and file name. Will attempt to contact the server and get the file and write
    it to a file (by default this is log.txt and can be changed by editing this
    source code). """
    ip_addr, port_num, file_name = getinfo() # Gather the three inputs
    ip_addr = validate_ip(ip_addr) # Validate IP
    port_num = validate_port(port_num) # Validate Port number 
    validate_file(file_name) # Validate file
    s = create_connect_socket(ip_addr, port_num) # Create socket and connect
    connection_msg(s) # Receive initial connection message
    file_request = create_filerequest(file_name) # Create file_request
    s.send(file_request) # Send the file request to the server
    data_text = receive_fileresponse(s) # Receive file from server
    write_to_file("log.txt", data_text) # Write to file

main()