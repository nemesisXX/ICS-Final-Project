# ICS-Final-Project
This program utilizes the basic chat system and encryption programming to communicate with our friends while preventing our chat information from being leaked. 
Nowadays, information leakage has become a serious problem, eavesdroppers intentionally steal information to use victims’ information as a harmful benefit. 
The most frequent case which results in eavesdropping is information delivery, more specifically, chat communication. 
Therefore, our motivation is to hold back the eavesdropping during the chat. The whole program can be divided into two parts. 
The first one is the basis of the chat system. The second part is the encryption and decryption program. 
For these two effects, we import Crypto.RSA and Crypto.Cipher.PKCS1_OAEP from PyCrypto(Python Cryptography Toolkit) and jsonpickle which is for the two-way conversion of complex Python objects and JSON.
**Note that this program has to execute under python 3.7 rather than python 3.8 since the PyCrypto doesn't support python 3.8**
