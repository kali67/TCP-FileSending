import socket
import sys
from random import*
import select
import pickle
import time
from packet import Packet


HOSTNAME = '127.0.0.1'

def check_port_number(port_number):
    """Check port number validity"""
    if (int(port_number) > 1024 and int(port_number) < 64000):
        return int(port_number)
    else:
        raise ValueError("port number must be in the range [{}. {}]".format(1024, 64000))

def main(argv):
    """Create the four sockets for the channel, these are TCP sockets,
        bound to local host and the entered port numbers"""
    cs_in, cs_out, cr_in, cr_out, s_in, r_in = map(check_port_number, argv[0:6])
    p_rate = argv[6]

    #creates and binds all the sockets for the channel
    try:
        c_sender_in = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        c_sender_in.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        c_sender_in.bind((HOSTNAME, cs_in))
        
        c_sender_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_sender_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        c_sender_out.bind((HOSTNAME, cs_out))
        
        c_receiver_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_receiver_in.bind((HOSTNAME, cr_in))
        
        c_receiver_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_receiver_out.bind((HOSTNAME, cr_out))
    except socket.error:
        print("Cannot create sockets! Exiting...")
        sys.exit()
        
    print("Channel ports successfully bound!")

    #Listens for the reciever 
    print("Listening for reciever....")
    c_receiver_in.listen(5)
    c_receiver_in_connection, c_receiver_in_address = c_receiver_in.accept()
    print("Got connection from {}".format(c_receiver_in_address))

    #Connects to the receiver in port
    try:
        c_receiver_out.connect((HOSTNAME, r_in))
        print("Channel connected to {}".format(r_in))
    except socket.error:
        print("Cannot connect! Exiting...")
        sys.exit()


    #Listens for the sender connection
    print("Listening for sender....")
    c_sender_in.listen(5)
    c_sender_in_connection, c_sender_in_address = c_sender_in.accept()
    print("Got connection from {}". format(c_sender_in_address))
    
    #Connects to the sender in port
    try:
        c_sender_out.connect((HOSTNAME, s_in))
        print("Channel connected to {}".format(s_in))
    except socket.error:
        print("Cannot connect! Exiting...")
        sys.exit()

    print("Waiting for the sender to send data....")

 
    sender_message = False
    while not sender_message:
        ready_to_read, _, _ = select.select([c_sender_in_connection, c_receiver_in_connection], [], [])
        for sock in ready_to_read:
            
            if sock == c_sender_in_connection:
                data = c_sender_in_connection.recv(1024)
                data_unpacked = pickle.loads(data) 
                u = uniform(0, 1)
                if u < p_rate:
                    print("Data packet dropped!")   
                else:
                    if data_unpacked.get_magic_no() != 0x497E:
                        print("No a valid packet!")
                        continue
                    elif data_unpacked.get_data_len() == 0:
                        print("No data or empty packet received!")
                        sender_message = True
                    else:# forward packet to receiver
                        v = uniform(0,1)
                        if v < 0.1: #introduce bit errors
                            data_unpacked.incrementDataLen(randint(0,10)) #increment the dataLen by randint 
                            #forwrd to the receiver
                        ser_packet = pickle.dumps(data_unpacked)
                        print("Packet from sender: {}".format(data_unpacked.get_packet_sequence_no()))
                        c_receiver_out.send(ser_packet)
                        
                
                        
            elif sock == c_receiver_in_connection:
                data_rec = c_receiver_in_connection.recv(1024)
                data_unpacked_rec = pickle.loads(data_rec)
                u_rec = uniform(0, 1)
                if u_rec < p_rate: #sender doesnt receive ack so retransmits
                    print("Data packet dropped!")
                    
                else:
                    v_rec = uniform(0,1)
                    if data_unpacked_rec.get_magic_no() != 0x497E:
                        print("Not a valid packet!")
                    else:# Send acknowledgement packet, nothin
                        if v_rec < 0.1: #introduce bit errors
                            data_unpacked_rec.incrementDataLen(randint(0,10)) #increment the dataLen by randint 
                        #forwrd to the sender
                        ser_packet = pickle.dumps(data_unpacked_rec)
                        print("Packet from receiver: {}".format(data_unpacked_rec.get_packet_sequence_no()))
                        c_sender_out.send(ser_packet)
                        
                     
                 

            
                   

    c_sender_in.close()
    c_sender_out.close()
    c_receiver_in.close()
    c_receiver_out.close()
    print("Closed all sockets!")
        
if __name__ == "__main__":
    main([10000,10001,10002,10003,10004,10058,0.3])
