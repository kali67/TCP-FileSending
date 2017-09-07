import socket
import os
import time
import pickle
from packet import Packet
import select

HOSTNAME = '127.0.0.1'


def check_port_number(port_number):
    """Check port number validity"""
    if (int(port_number) > 1024 and int(port_number) < 64000):
        return int(port_number)
    else:
        raise ValueError("port number must be in the range [{}. {}]".format(1024, 64000))
 
def main(argv):

    s_in = check_port_number(argv[0])
    s_out = check_port_number(argv[1])
    c_s_in = check_port_number(argv[2])
    file_name = argv[3]
    
    #create and bind all of the sender sockets
    sender_in = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sender_in.bind((HOSTNAME, s_in))
    sender_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender_out.bind((HOSTNAME, s_out))


    #sender to channel connection
    sender_out.connect((HOSTNAME, c_s_in))
    print("Sender connected to {}".format(c_s_in))

    #listen for channel to sender connection
    sender_in.listen(5)
    sender_in_connection, sender_in_address = sender_in.accept()
    print("Got connection from {}".format(sender_in_address))
        
    try:
        file_in = open(file_name, 'rb')
    except IOError:
        exit()

    next_ = 0
    exit_flag = False
    text_position = 0
    sequence_no = 0
    bytestream_packets_buffer = []
    while not exit_flag:
        file_in.seek(text_position) #go to the position in the file
        data_to_be_sent = file_in.read(512) # read 512 bytes of data from the file
        if len(data_to_be_sent) == 0:
            packet_to_send = Packet(0x497E, 0, data_to_be_sent, 0, None) #create a new packet
            exit_flag = True # terminate because no more data to be read
        else:
            packet_to_send = Packet(0x497E, 0, sequence_no, len(data_to_be_sent), data_to_be_sent) # create new packet
            text_position += 512 # adjust file position

        bytestream_packet = pickle.dumps(packet_to_send) #serialises packet as string object rather than writing to a file
        confirmation_received = False
        while not confirmation_received: # waits for ack from the channel before sending the next packet
            sender_out.send(bytestream_packet)
            time.sleep(0.3)
            ready,_,_ = select.select([sender_in_connection], [], [], 1)
            print("Packet has been sent!")
            if sender_in_connection in ready:
                data = sender_in_connection.recv(1024)
                data = pickle.loads(data)
                if data.get_packet_sequence_no() == sequence_no:
                    sequence_no += 1
                    confirmation_received = True

                else:
                   print("Packet mismatch, retransmitting")
       

if __name__ == "__main__":
    main([10004, 10005, 10000, "text.txt"]);
        
    
