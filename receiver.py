import socket
import sys
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
    r_in, r_out, cr_in= map(check_port_number, argv[0:3])
    file_name = argv[3]

    file_write = open(file_name, 'a')
    
    #create and bind all of the reciever sockets
    r_in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r_in_sock.bind((HOSTNAME,r_in))
    r_out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r_out_sock.bind((HOSTNAME, r_out))
    
    print("Receiver sockets successfully initialized and bound!")


    #connect to the cr_in port
    r_out_sock.connect((HOSTNAME, cr_in))
    print("Receiver connected to {}". format(cr_in))

    
    #listen and wait for a response
    print("Listening for channel....")
    r_in_sock.listen(5)
    r_in_sock_connection, r_in_sock_address = r_in_sock.accept()
    print("Got connection from {}".format(r_in_sock_address))
    
    received_message = False
    while not received_message:
        ready,_,_ = select.select([r_in_sock_connection], [], [])
        if r_in_sock_connection in ready:
            # Receives message from sender
            print("Packet received")
            data = r_in_sock_connection.recv(1024)
            try:
                data = pickle.loads(data)
                return_no = data.get_packet_sequence_no()
                if data.get_data_len() == 0:
                    print("No data or empty packet received!")
                    received_message_c = True
                else:
                    #print("Received; seqno:{}\n".format(data))
                    # Send acknowledgement packet
                    file_write.write(data.get_packet_payload().decode("utf-8") ) #write data to file
                    
                    acknowledgement_packet = Packet(0x497E, 1, return_no, 0, None)
                    bytestream_packet = pickle.dumps(acknowledgement_packet)
                    r_out_sock.send(bytestream_packet)
                    print("Sent ack to channel")
            except EOFError as e:
                file_write.close()
                print("Closed File", e)


    r_in_sock.close()
    r_out_sock.close()
    
    
        


if __name__ == "__main__":
    main([10006, 10007, 10002, "test.txt"]);
