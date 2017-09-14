class Packet():
    def __init__ (self, magicno, p_type, seqno, dataLen, data):
        self.magicno = magicno
        data_packet = 0
        acknowledgement_packet = 1
        self.p_type = p_type
        self.seqno = seqno
        self.dataLen = dataLen
        self.data = data


    def __str__(self):
        return "Packet: (MagicNo: {} Type: {} Seq No: {} Data Len:{} Payload: {})".format(self.get_magic_no(), self.get_packet_type(), self.get_packet_sequence_no(), self.get_data_len(), self.get_packet_payload())

    def get_magic_no(self):
        return self.magicno

    def incrementDataLen(self, x):
        self.dataLen += x
        
    def get_data_len(self):
        return self.dataLen
    
    def get_packet_type(self):
        return self.p_type

    def get_packet_payload(self):
        return self.data
    
    def get_packet_sequence_no(self):
        return self.seqno

    
        
