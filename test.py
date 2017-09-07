import pickle
from packet import Packet
file_in = open("text.txt", 'rb')
file = open("receiver.txt", 'w')
next_ = 0
exit_flag = False
text_position = 0
sequence_no = 0

while not exit_flag:
    file_in.seek(text_position) #go to the position in the file
    data_to_be_sent = file_in.read(512) # read 512 bytes of data from the file
    print(len(data_to_be_sent))
    if len(data_to_be_sent) == 0:
        packet_to_send = Packet(0x497E, 0, data_to_be_sent, 0, None) #create a new packet
        exit_flag = True # terminate because no more data to be read
    else:
        packet_to_send = Packet(0x497E, 0, sequence_no, len(data_to_be_sent), data_to_be_sent) # create new packet
        text_position += 512 # adjust file position

    bytestream_packet = pickle.dumps(packet_to_send) #serialises packet as string object rather than writing to a file
    data = pickle.loads(bytestream_packet)
    

    
    print(data)
file.write("HELLO WORLD")
file.close()
