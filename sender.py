import socket
import os
import time
import sys
import pickle
from packet import Packet
import select

HOSTNAME = '127.0.0.1'

def check_port_number(port_number):
    """Check port number validity"""
    if (int(port_number) > 1024 and int(port_number) < 64000):
        return int(port_number)
    else:
        print("Port numbers must be in the range (1024, 64000)")
        sys.exit()
    
def valid_ack_packet(data, next_):
    if data.get_packet_sequence_no() == next_ and data.get_packet_type() == 1:
        if data.get_data_len() == 0 and data.get_magic_no() == 0x497E:
            return True
        else:
            return False

def close_program(file_in, sender_in, sender_out, packets_sent):
    file_in.close()
    sender_in.close()
    sender_out.close()
    print("Total number of packets sent: {}", packets_sent)
    sys.exit()

def main(*argv):
    s_in = check_port_number(argv[0])
    s_out = check_port_number(argv[1])
    c_s_in = check_port_number(argv[2])
    file_name = argv[3]
    #create and bind all of the sender sockets
    try:
        sender_in = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sender_in.bind((HOSTNAME, s_in))
        sender_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_out.bind((HOSTNAME, s_out))
    except socket.error:
        print("Cannot create and bind sockets! Exiting...")
        sys.exit()
        
    #sender to channel connection
    try:
        sender_out.connect((HOSTNAME, c_s_in))
        print("Sender connected to {}".format(c_s_in))
    except socket.error:
        sys.exit("Cannot connect! Exiting...")

    #listen for channel to sender connection
    sender_in.listen(5)
    sender_in_connection, sender_in_address = sender_in.accept()
    print("Got connection from {}".format(sender_in_address))
        
    try:
        file_in = open(file_name, 'rb')
    except IOError:
        sys.exit("File cannot be found. Exiting...")

    next_ = 0
    exit_flag = False
    text_position = 0
    packets_sent = 0
    while not exit_flag:
        file_in.seek(text_position) #go to the position in the file
        data_to_be_sent = file_in.read(512) # read 512 bytes of data from the file
        if len(data_to_be_sent) == 0:
            print("No more data to be sent! Sending empty packet..")
            packet_to_send = Packet(0x497E, 0, next_, 0, None)
            exit_flag = True
        else:
            packet_to_send = Packet(0x497E, 0, next_, len(data_to_be_sent), data_to_be_sent)
            text_position += 512 # adjust file position
        bytestream_packet = pickle.dumps(packet_to_send) 
        confirmation_received = False
        while not confirmation_received:
            try:
                sender_out.send(bytestream_packet)
                print("Packet {} sent!".format(packets_sent))
                packets_sent += 1
                ready,_,_ = select.select([sender_in_connection], [], [], 1)#wait for response
                if sender_in_connection in ready:
                
                    data_received = sender_in_connection.recv(1024)
                    data_received = pickle.loads(data_received)
                    if (valid_ack_packet(data_received, next_)):
                        next_ += 1
                        confirmation_received = True
                    else:
                        print("Packet mismatch, retransmitting")
            except EOFError:
                print("Cannot load from empty file!Exiting...")
                close_program(file_in, sender_in, sender_out, packets_sent)
            except socket.error as e: #read from empty file.
                print(e)
                print("Exiting...")
                close_program(file_in, sender_in, sender_out, packets_sent)        
                     
if __name__ == "__main__":
    main(10004, 10005, 10000, "text.2.txt") #for testing
