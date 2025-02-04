# Reliable-Data-Transmission-over-an-Unreliable-Network


This assignment concerns the problem of delivering information reliably across a network where a
degree of packet loss is expected. In the assignment, two programs cooperate in the reliable transfer
of a file, using UDP datagrams, in an environment where data and acknowledgment datagrams can
be (and will be) lost. The application is composed of two processes:
• Sender: sends the contents of the file in blocks of fixed size to a receiver process located in
another machine
• Receiver: receives the blocks of the file knowingly each block received
Sender and receiver handle the loss of data and acknowledge using a sliding window of dimension N
and Go-Back-N strategy. Just like in lab05, the transfer must be done by sending chunks of the file,
with the size of the chunks being defined by the client.


Project PDF:

[Lab06_TPC2.pdf](https://github.com/user-attachments/files/18660971/Lab06_TPC2.pdf)
