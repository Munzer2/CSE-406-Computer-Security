import hashlib
import random
import socket
import struct
_util1 = __import__('2005018_task1')
_util2 = __import__('2005018_task2')
_utils = __import__('2005018_utils')
setup = _util2._setup
scalarMul = _util2._scalarMul

def _sendMssg(sock, num): 
    num_str = str(num) 
    _data = num_str.encode('utf-8')
    sz = len(_data) 
    size_data = struct.pack('>I', sz)
    sock.sendall(size_data) 
    sock.sendall(_data)

def _recvMssg(sock): 
    sz_data = sock.recv(4)
    sz = struct.unpack('>I', sz_data)[0]
    num_data = sock.recv(sz)
    number_str = num_data.decode('utf-8')
    num = int(number_str)
    return num

def _sendBytes(sock, _data): 
    sz_data = struct.pack('>I', len(_data))
    sock.sendall(sz_data)
    sock.sendall(_data)

def _recvBytes(sock): 
    sz_data = sock.recv(4)
    sz =struct.unpack('>I', sz_data)[0]
    _data = sock.recv(sz)
    return _data

def runAlice(host = 'localhost', port = _utils.PORT, bitLen = 128): 
    P, a ,b, G = setup(bitLen)
    kA = random.randrange(1, P) 
    Ax, Ay = scalarMul(kA, G, a , P)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Alice Connected to {host}: {port}")

        _sendMssg(s,P)
        _sendMssg(s,a)
        _sendMssg(s,b)
        _sendMssg(s,G[0])
        _sendMssg(s,G[1])
        _sendMssg(s,Ax)
        _sendMssg(s,Ay)

        Bx = _recvMssg(s)
        By = _recvMssg(s)

        key, _ = scalarMul(kA , (Bx, By), a, P)
        _hash_res = hashlib.sha256(str(key).encode()).digest()
        key_bytes = bitLen // 8
        _key = _hash_res[:key_bytes]


        s.sendall(b'READY')

        if s.recv(5) != b'READY': 
            print("Problems faced. Bye!")
            return 
        
        plaintext = "We need picnic" 
        roundKeys = _util1.keyExpansion(_key) 
        cipherTextBytes = _util1.aes_enc_CBC(plaintext, roundKeys, 10) 
        # print(cipherTextBytes) 
        _sendBytes(s, cipherTextBytes)


runAlice()
