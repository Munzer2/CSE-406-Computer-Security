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

def _runBob(host='localhost', port=_utils.PORT, bitLen=128):
    P, a, b, G = setup(bitLen)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)

        print(f"Bob listening on {host}: {port}")

        conn, addr = s.accept()
        with conn:
            print(f"Bob connected by {addr}")

            P = _recvMssg(conn)
            a = _recvMssg(conn)
            b = _recvMssg(conn)
            Gx = _recvMssg(conn)
            Gy = _recvMssg(conn)
            Ax = _recvMssg(conn)
            Ay = _recvMssg(conn)

            Kb = random.randrange(1, P)
            Bx, By = scalarMul(Kb, (Gx, Gy), a, P)

            keyX, _ = scalarMul(Kb, (Ax, Ay), a, P)
            key = hashlib.sha256(str(keyX).encode()).digest()
            key_bytes = bitLen // 8
            key = key[:key_bytes]
            roundKeys = _util1.keyExpansion(key)
            
            _sendMssg(conn, Bx)
            _sendMssg(conn, By)


            if(conn.recv(5) != b'READY') : 
                print("Problems faced. Bye!")
                return 
            conn.sendall(b'READY')


            ciphertextBytes = _recvBytes(conn)
            # print(ciphertextBytes) 
            plaintext_bytes = _util1.aes_dec_CBC(ciphertextBytes, roundKeys, 10)
            final_plainText = _util1.pkcs7_unpad(plaintext_bytes).decode('utf-8')
            print(final_plainText)
            


_runBob()