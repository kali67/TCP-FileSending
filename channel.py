import socket
import sys
from random import*
import select
import pickle
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

    print("Channel ports successfully bound!")

    #Listens for the reciever 
    print("Listening for reciever....")
    c_receiver_in.listen(5)
    c_receiver_in_connection, c_receiver_in_address = c_receiver_in.accept()
    print("Got connection from {}".format(c_receiver_in_address))

    #Connects to the receiver in port
    c_receiver_out.connect((HOSTNAME, r_in))
    print("Channel connected to {}".format(r_in))


    #Listens for the sender connection
    print("Listening for sender....")
    c_sender_in.listen(5)
    c_sender_in_connection, c_sender_in_address = c_sender_in.accept()
    print("Got connection from {}". format(c_sender_in_address))
    
    #Connects to the sender in port
    c_sender_out.connect((HOSTNAME, s_in))
    print("Channel connected to {}".format(s_in))
    

    print("Waiting for the sender to send data....")

    
    sender_message = False

    while not sender_message:
        ready_to_read, _, _ = select.select([c_sender_in_connection, c_receiver_in_connection], [], [])
        for sock in ready_to_read:
            if sock == c_sender_in_connection:
                data = c_sender_in_connection.recv(1024)
                data_unpacked = pickle.loads(data) #causes error, runs out of data, EOFError 
                return_no = data_unpacked.get_packet_sequence_no()
                u = uniform(0, 1)
                if u < p_rate: #sender doesnt receive ack so retransmits
                    print("Data packet dropped!")
                else:
                    v = uniform(0,1)
                    if data_unpacked.get_magic_no() != 0x497E:
                        print("No a valid packet!")
                    elif data_unpacked.get_data_len() == 0:
                        print("No data or empty packet received!")
                        sender_message = True
                    else:# Send acknowledgement packet, nothin
                        if v < 0.1: #introduce bit errors
                            data_unpacked.incrementDataLen(randint(0,10)) #increment the dataLen by randint 

                        #send ack packet    
                        print("Received; seqno:{}\n".format(data_unpacked.get_packet_sequence_no()))
                        acknowledgement_packet = Packet(0x497E, 1, return_no, 0, None)
                        bytestream_packet = pickle.dumps(acknowledgement_packet)
                        c_sender_out.send(bytestream_packet)
                        #ack packet sent, now must forward to the receiver
                        ser_packet = pickle.dumps(data_unpacked)
                        c_receiver_out.send(ser_packet)
                        print("Sent packet to the receiver!")
                        
            elif sock == c_receiver_in_connection:
                 print("Packet received from receiver!")
                 

            
                   

    c_sender_in.close()
    c_sender_out.close()
    c_receiver_in.close()
    c_receiver_out.close()
        
if __name__ == "__main__":
    main([10000,10001,10002,10003,10004,10006,0.3])
