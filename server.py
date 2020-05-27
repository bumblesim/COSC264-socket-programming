import socket
import sys
import os.path
from time import strftime

"""
server.py
COSC264 Socket Assignment
Author: Simon Lorimer
ID: 34339189
"""

def check_port(port_num):
    """ Ensures that the number specified is between 1024 and 64000 (included).
    If correct, will return the number, else will exit the program. """
    #Check Port number is within bounds, if not the program will exit
    if ((int(port_num) < 1024) or (int(port_num) > 64000)):
        sys.exit(port_num + " is an incorrect port value.\nThe program will now exit.")
    return port_num

def get_port():
    """ Asks the user to input in a port number. Once done, will call 
    check_port() """ 
    #Get the Port number, if input is non-Integer the program will exit
    try:  
        port_num = int(input("Please enter the port to bind to: "))
    except:
        sys.exit("Invalid Port.\nThe program will now exit.")
    return check_port(port_num)

def create_bind_socket(port_num):
    """ Attempts to create a socket and bind. Returns the socket once created. 
    """
    s = socket.socket(socket.AF_INET, socket. SOCK_STREAM)
    s.bind((socket.gethostname(), port_num))
    return s

def established(address, port):
    """ Prints the time, as well as the address and port that the connection
    has been established from. """
    time = strftime("%H:%M:%S")
    print(f"{time}: Connection from address {address} from port {port} has been established!")
    return

def receive_filerequest(clientsocket):
    """ Breaks down received bytes to check the header and returns the file_name. """
    magic_one = str(hex(clientsocket.recv(1)[0])) + str(hex(clientsocket.recv(1)[0]))[-2:]
    magic_int_num = int(magic_one, 16)
    magic_num = hex(magic_int_num)
    #print(int(magic_num))
    if magic_int_num != 18814:
        sys.exit("Invalid Magic number.\nThe program will now exit.")
    pkt_type = int(clientsocket.recv(1)[0])
    if pkt_type != 1:
        sys.exit("Invalid Packet type.\nThe program will now exit.")
    
    file_len = int.from_bytes(clientsocket.recv(2), byteorder = "big", signed = False)
    file_name = clientsocket.recv(file_len).decode("utf-8")
    return file_name

def read_file(file_name):
    """ Returns the string of the file. """
    open_file = open(file_name, "r")
    text = open_file.read()
    return text

def prepare_fileresponse(file_name):
    """ Prepares the FileResponse to be sent to the client. Returns a bytearray
    ordered in the format of the FileResponse """
    file_response = bytearray()
    magic_num = 0x497e # Magic Number
    file_response.extend(magic_num.to_bytes(2, byteorder = "big"))
    
    pkt_type = 2 # Packet Type number
    file_response.extend(pkt_type.to_bytes(1, byteorder = "big"))
    
    status_code = 1 # Status Code unless changed by incorrect file
    
    #Validate file
    print(f"Received response for {file_name}, processing...")
    if os.path.isfile(file_name) is False:
        status_code = 0
    file_response.extend(status_code.to_bytes(1, byteorder = "big"))
    
    text = read_file(file_name) # Read file for String
    file_len = len(text)
    file_response.extend(file_len.to_bytes(4, byteorder = "big"))
    
    ascii_text = [ord(each) for each in text]
    for each in ascii_text:
        file_response.extend(each.to_bytes(1, byteorder = "big"))
        
    return file_response

def main():
    """ Main function of the program. This mostly calls other functions and acts
    as a fully functional server. Asks the user to input a port number. It will
    bind to that port and attempt to send any file requests from a client. """
    port_num = get_port()
    s = create_bind_socket(port_num)
    
    try:
        s.listen(5) # Attempt to listen, else exit program
    except:
        s.close()  
        sys.exit("An error occured while listening.\nThe program will now exit.")
                        
    while True:
        clientsocket, (address, port) = s.accept()  
        established(address, port) # Prints successful
        clientsocket.send(bytes("Connection established with server.", "utf-8"))
        file_name = receive_filerequest(clientsocket) # Receive the FileRequest
        file_response = prepare_fileresponse(file_name) # Prepare FileResponse
        clientsocket.send(file_response) # Send File Response
        time = strftime("%H:%M:%S")
        print(f"{time}: File {file_name} has been sent!")         
    
main()