# TCP-FileTransfer

A sender will sender a file split into packets of data size 512 bytes. Packet is then sent to a channel which simulates packet loss and introduces bit errors. The packet is then forwarded to the receiver where an ack is sent back through the channel then forwarded to the sender. A md5 checksum is also calculated for each packet that is sent and then recalulated at the receiver to check if any bit errors have been introduced. If so, the packet will be dropped by the receiver then re-transmitted.

