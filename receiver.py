import socket
import sys
import select
import pickle
from packet import Packet
import time
import os

HOSTNAME = '127.0.0.1'

def check_port_number(port_number):
    """Check port number validity"""
    if (int(port_number) > 1024 and int(port_number) < 64000):
        return int(port_number)
    else:
        print("Port numbers must be in the range (1024, 64000)")
        sys.exit()

    
def send_ack(r_out_sock, return_no):
    acknowledgement_packet = Packet(0x497E, 1, return_no, 0, None)
    bytestream_packet = pickle.dumps(acknowledgement_packet)
    r_out_sock.send(bytestream_packet)

def close_program(r_in_sock, r_out_sock, file_write):
    r_in_sock.close()
    r_out_sock.close()
    file_write.close()
    print("Closed all sockets!")
    sys.exit()
 
def main(*argv):
    """Create the four sockets for the channel, these are TCP sockets,
        bound to local host and the entered port numbers"""
    r_in, r_out, cr_in= map(check_port_number, argv[0:3])
    file_name = argv[3]
    
    if(os.path.isfile(file_name)):
        print("Sorry, file already exists! Please delete it and try again.")
        sys.exit()
    
    file_write = open(file_name, 'a+b')

    #create and bind all of the reciever sockets
    try:
        r_in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        r_in_sock.bind((HOSTNAME,r_in))
        r_out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        r_out_sock.bind((HOSTNAME, r_out))
    except socket.error:
        print("Cannot create sockets! Exiting...")
        sys.exit()
        
    print("Receiver sockets successfully initialized and bound!")


    #connect to the cr_in port
    try:
        r_out_sock.connect((HOSTNAME, cr_in))
        print("Receiver connected to {}". format(cr_in))
    except socket.error:
        print("Cannot connect! Exiting...")
        sys.exit()
        
    
    #listen and wait for a response
    print("Listening for channel....")
    r_in_sock.listen(5)
    r_in_sock_connection, r_in_sock_address = r_in_sock.accept()
    print("Got connection from {}".format(r_in_sock_address))

    expected = 0
    received_message = False
    while not received_message:
        ready,_,_ = select.select([r_in_sock_connection], [], [])
        if r_in_sock_connection in ready:
            print("Packet received")
            data = r_in_sock_connection.recv(1024)
            try:
                data = pickle.loads(data)
                seqno = data.get_packet_sequence_no()
                if  data.getChecksum() != data.calculateChecksum(): 
                    print("BIT ERROR. RETRANSMITTING!")
                elif data.get_magic_no() != 0x497E or data.get_packet_type() != 0:
                    print("Error in packet, retransmitting!")
                elif data.get_data_len() == 0:
                    print("No data or empty packet received!")
                    send_ack(r_out_sock, seqno)
                    received_message = True
                elif expected != data.get_packet_sequence_no():
                    print("Duplicate packet! Sending ack")
                    send_ack(r_out_sock, seqno)
                else:
                    expected += 1
                    file_write.write(data.get_packet_payload())
                    print("Packet from sender: {}".format(data.get_packet_sequence_no()))
                    send_ack(r_out_sock, seqno)
            except EOFError:
                    file_write.close()
                    received_message = True
            except socket.error:
                    print("Cannot send to channel. Program exiting...")
                    close_program(r_in_sock, r_out_sock, file_write)
                    
    close_program(r_in_sock, r_out_sock, file_write)

if __name__ == "__main__":
    main(10058, 10007, 10002, "output.txt");
