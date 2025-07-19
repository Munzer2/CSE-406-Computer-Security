# author: Munzer Mahmood


import os
import time
_util = __import__('2005018_utils')
keySize = 128
params = _util.key_params[keySize]

AES_modulus = _util.BitVector(bitstring='100011011')  # AES irreducible polynomial

def ByteToWord(ByteKey):
    ans = []
    for i in range(0, len(ByteKey), 4):
        ans.append(ByteKey[i] << 24 | ByteKey[i + 1] << 16 | ByteKey[i + 2] << 8 | ByteKey[i + 3])

    return ans


def WordToByte(_words):
    return b''.join(word.to_bytes(4, byteorder = 'big') for word in _words) 


def SubWord(word):
    return (_util.Sbox[(word >> 24) & 0xFF] << 24 | _util.Sbox[(word >> 16) & 0xFF] << 16 | _util.Sbox[(word >> 8) & 0xFF] << 8 | _util.Sbox[word & 0xFF])

def RotWord(word):
    return ((word << 8) | (word >> 24)) & 0xFFFFFFFF # ensuring the result stays within 32-bits


def _genRcon(Rounds):
    rcon = [0x00000000] 
    curr = 0x01000000 # rcon[1]

    for i in range(1,Rounds):
        rcon.append(curr)
        _next = curr << 1
        if curr & 0x80000000:
            _next ^= 0x1B000000
        curr = _next & 0xFFFFFFFF
    return rcon

def keyExpansion(ByteKey):
    params = _util.key_params[len(ByteKey)*8]
    colCnt = params['colCnt']
    wCnt = 4
    Rounds = params['Rounds']
    rcon = _genRcon(Rounds)


    w = [0] * (Rounds * wCnt)
    _W = ByteToWord(ByteKey)

    for i in range(colCnt):
        w[i] = _W[i] 

    for i in range (colCnt, Rounds * wCnt): 
        temp = w[i - 1]
        if (i % colCnt == 0):
            temp = SubWord(RotWord(temp)) ^ rcon[i // colCnt]
        elif colCnt == 8 and i % colCnt == 4:
            temp = SubWord(temp)
        w[i] = w[i-colCnt] ^ temp

    ans = []
    for i in range(0, len(w), wCnt):
        ans.append(WordToByte(w[i:i+wCnt]))
    return ans


def pkcs7_pad(plaintext_bytes, block_size = 16):
    padLen = block_size - len(plaintext_bytes) % block_size
    return plaintext_bytes + bytes([padLen] * padLen)

def pkcs7_unpad(data):
    padLen = data[-1]
    if padLen < 1 or padLen > 16: 
        print("Invalid padding.\n")
    elif data[-padLen:] != bytes([padLen]*padLen):
        print("Invalid padding.\n")
    else: 
        return data[:-padLen]

def _hex_list(keyBytes):
    return [f'{byte:02x}' for byte in keyBytes]

def adjustKey(key, _len):
    key = key.encode('utf-8')
    keyLen = _len // 8 # in bytes
    if len(key) < keyLen:
        return key.ljust(keyLen, b'\x00')
    else:
        return key[:keyLen] 

def bytesToMatrix(bytes ):
    return [ [bytes[row + 4*col] for col in range(4)] for row in range(4) ]


def addRoundKey(state, roundKeyMatrix):  
    for i in range(len(state)):
        for j in range(len(state[0])):
            state[i][j] ^= roundKeyMatrix[i][j]
    return state

def subBytes(state_matrix):
    rows,cols = len(state_matrix), len(state_matrix[0])
    for i in range(rows):
        for j in range(cols):
            state_matrix[i][j] = _util.Sbox[state_matrix[i][j]]
    return state_matrix

def inv_subBytes(state_matrix):
    rows,cols = len(state_matrix), len(state_matrix[0])
    for i in range(rows):
        for j in range(cols):
            state_matrix[i][j] = _util.InvSbox[state_matrix[i][j]]
    return state_matrix

def shiftRows(state_matrix):
    for i in range(1,len(state_matrix)):
        state_matrix[i] = state_matrix[i][i:] + state_matrix[i][:i]
    return state_matrix

def inv_shiftRows(state_matrix):
    rows= len(state_matrix)
    for i in range(rows): 
        state_matrix[i] = state_matrix[i][-i:] + state_matrix[i][:-i]
    return state_matrix

def mixColumns(state):
    for col in range(len(state[0])):
        col_vec = [_util.BitVector(intVal=state[row][col], size=8) for row in range(len(state))]
        new_col = []

        for i in range(len(state)):  
            result = _util.BitVector(intVal=0, size=8)
            for j in range(len(state[0])):
                result ^= _util.Mixer[i][j].gf_multiply_modular(col_vec[j], AES_modulus, 8)
            new_col.append(int(result))

        for row in range(len(state)):
            state[row][col] = new_col[row]

    return state
    
def inv_mixColumns(state):
    for col in range(len(state[0])):
        col_vec = [_util.BitVector(intVal=state[row][col], size=8) for row in range(len(state))]
        new_col = []

        for i in range(len(state)):
            result = _util.BitVector(intVal=0, size=8)
            for j in range(len(state[0])):
                result ^= _util.InvMixer[i][j].gf_multiply_modular(col_vec[j], AES_modulus, 8)
            new_col.append(int(result))

        for row in range(len(state)):
            state[row][col] = new_col[row]

    return state
        


def AES_encryption(bytes_array, allroundkeys,rounds):
    # print(bytes_array) 
    state_matrix = bytesToMatrix(bytes_array)
    # print_matrix_inHex(state_matrix)
    allRoundKeyMatrices = [bytesToMatrix(roundKey) for roundKey in allroundkeys]
    state_matrix = addRoundKey(state_matrix, allRoundKeyMatrices[0])
    # print("Initial Round") 
    # print_matrix_inHex(state_matrix)
    # print()
    for round in range(1, rounds):
        state_matrix = subBytes(state_matrix)
        state_matrix = shiftRows(state_matrix)
        state_matrix = mixColumns(state_matrix)
        state_matrix = addRoundKey(state_matrix,allRoundKeyMatrices[round])
        # print("Round " + str(round))
        # print_matrix_inHex(state_matrix)
        # print()

    # no mix columns in the last round
    # print("Final round")
    state_matrix = subBytes(state_matrix)
    state_matrix = shiftRows(state_matrix)
    state_matrix = addRoundKey(state_matrix,allRoundKeyMatrices[rounds])
    # print_matrix_inHex(state_matrix)
    # print()
    return matrixToBytes(state_matrix)

def AES_decryption(ciphertext_bytes, allroundkeys, rounds):
    # print(bytes_array) 
    state_matrix = bytesToMatrix(ciphertext_bytes)
    # print_matrix_inHex(state_matrix)
    allRoundKeyMatrices = [bytesToMatrix(roundKey) for roundKey in allroundkeys]
    state_matrix = addRoundKey(state_matrix, allRoundKeyMatrices[rounds]) # start from last round key
    # print("Initial Round") 
    # print_matrix_inHex(state_matrix)
    # print()
    for round in range(rounds-1, 0, -1):
        state_matrix = inv_shiftRows(state_matrix)
        state_matrix = inv_subBytes(state_matrix)
        state_matrix = addRoundKey(state_matrix,allRoundKeyMatrices[round])
        state_matrix = inv_mixColumns(state_matrix)
        # print("Round " + str(round))
        # print_matrix_inHex(state_matrix)
        # print()

    # no mix columns in the last round
    # print("Final round")
    state_matrix = inv_shiftRows(state_matrix)
    state_matrix = inv_subBytes(state_matrix)
    state_matrix = addRoundKey(state_matrix,allRoundKeyMatrices[0])
    # print_matrix_inHex(state_matrix)
    # print()
    return matrixToBytes(state_matrix)

def matrixToBytes(state_matrix):
    return bytes([state_matrix[row][col] for col in range(len(state_matrix[0])) for row in range(len(state_matrix))])

def print_matrix_inHex(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(f'{matrix[i][j]:02x}', end=' ')
        print()

def printKeys(roundKeys):
    for roundkey in roundKeys:
        hexkey = _hex_list(roundkey)
        for c in hexkey:
            print(c, end = ' ')
        print()


def aes_enc_CBC(plaintext, allroundKeys, rounds):
    if __name__ == '__main__': 
        print("Plain Text: ")
        print("In ASCII: " + plaintext)
        print("In Hex:", end = ' ')
        for c in _hex_list(plaintext.encode('utf-8')):
            print(c, end = ' ')
        print()
    plaintext_bytes = plaintext.encode('utf-8')
    bytes_array = pkcs7_pad(plaintext_bytes)
    if __name__ == '__main__': 
        print("In ASCII (After Padding): " + bytes_array.decode('utf-8'))
        print("In Hex(After Padding):", end = ' ')
        for c in _hex_list(bytes_array):
            print(c, end = ' ')
        print("\n\n")
    cipher_blocks = []
    iv = os.urandom(16)
    prev_block = iv
    for block in range(0, len(bytes_array), 16):
        curr_block = bytes_array[block:block+16]
        xored_block = bytes([curr ^ prev for curr,prev in zip(curr_block, prev_block)])
        curr_cipher_block = AES_encryption(xored_block,allroundKeys,rounds)
        cipher_blocks.append(curr_cipher_block)
        prev_block = curr_cipher_block

    return iv + b''.join(cipher_blocks)


def aes_dec_CBC(ciphertext_bytes, allroundkeys, rounds):
    IV = ciphertext_bytes[:16]
    ciphertext_bytes = ciphertext_bytes[16:]
    plaintext = b''
    prev_block = IV
    for i in range(0, len(ciphertext_bytes), 16):
        cipher_block = ciphertext_bytes[i:i+16]
        decrypted_block = AES_decryption(cipher_block,allroundkeys,rounds) 
        plain_block = bytes([dec ^ prev for dec,prev in zip(decrypted_block,prev_block)])
        plaintext += plain_block
        prev_block = cipher_block
    return plaintext


def _fileHandling(): 
    print("Input your key: ")
    key = input()
    print("Key: ")
    print("In ASCII: " + key) 
    print("In HEX:", end = ' ')
    for c in _hex_list(key.encode('utf-8')):
        print(c, end = ' ')
    print('\n\n')
    key = adjustKey(key , keySize)
    roundKeys = keyExpansion(key)

    with open('test.jpg', 'rb') as f : 
        data = f.read() 
    bytes_array = pkcs7_pad(data)
    # print("In ASCII (After Padding): " + bytes_array.decode('utf-8'))
    # print("In Hex(After Padding):", end = ' ')
    # for c in _hex_list(bytes_array):
    #     print(c, end = ' ')
    # print("\n\n")
    cipher_blocks = []
    iv = os.urandom(16)
    prev_block = iv
    for block in range(0, len(bytes_array), 16):
        curr_block = bytes_array[block:block+16]
        xored_block = bytes([curr ^ prev for curr,prev in zip(curr_block, prev_block)])
        curr_cipher_block = AES_encryption(xored_block,roundKeys,params['Rounds']-1)
        cipher_blocks.append(curr_cipher_block)
        prev_block = curr_cipher_block

    _ciphered = iv + b''.join(cipher_blocks)


    _ans = aes_dec_CBC(_ciphered, roundKeys, params['Rounds']-1)
    _ans = pkcs7_unpad(_ans) 
    with open("result.jpg", 'wb') as out:
        out.write(_ans) 
    


def _handlePlain():
    # key = "BUET CSE20 Batch"
    print("Input your key: ")
    key = input()
    plaintext = "We need picnic" 

    print("Key: ")
    print("In ASCII: " + key) 
    print("In HEX:", end = ' ')
    for c in _hex_list(key.encode('utf-8')):
        print(c, end = ' ')
    print('\n\n')

    _start_keyExpansion = time.perf_counter()
    key = adjustKey(key , keySize)
    roundKeys = keyExpansion(key)
    _end_keyExpansion = time.perf_counter()
    key_time = (_end_keyExpansion - _start_keyExpansion)*1000
    # printKeys(roundKeys)

    _strt_enc = time.perf_counter()
    ciphertext_bytes = aes_enc_CBC(plaintext, roundKeys,params['Rounds']-1)
    _end_enc = time.perf_counter()
    enc_time = (_end_enc - _strt_enc)*1000

    print("Ciphered text:") 
    print("In HEX:", end = ' ')
    for c in _hex_list(ciphertext_bytes):
        print(c, end = ' ')
    print("\nIn ASCII:", ciphertext_bytes.decode('latin1') + "\n\n")
    # print(ciphertext_bytes) 

    print("Deciphered text:")
    _strt_dec = time.perf_counter() 
    plaintext_bytes = aes_dec_CBC(ciphertext_bytes, roundKeys, params['Rounds']-1)
    _end_dec = time.perf_counter()
    dec_time = (_end_dec - _strt_dec ) * 1000
    print("Before Unpadding: ")
    print("In HEX:", end = ' ')
    for c in _hex_list(plaintext_bytes):
        print(c, end = ' ')
    print("\nIn ASCII: ", end = ' ')
    print(plaintext_bytes.decode('utf-8'))
    final_plainText = pkcs7_unpad(plaintext_bytes).decode('utf-8')
    print("After unpadding:")
    print("In ASCII: " + final_plainText)
    print("In HEX: " , end = ' ')
    for c in _hex_list(final_plainText.encode('utf-8')):
        print(c, end = ' ')
    print("\n\n")
    print("Execution Time Details: ")
    print(f"Key Schedule Time: {key_time:.3f} ms")
    print(f"Encryption Time: {enc_time:.3f} ms")
    print(f"Decryption Time:{dec_time:.3f} ms")



if __name__ == "__main__":
    _handlePlain() 
    # _fileHandling()


# key = "Buet CSE batch 20" 
# key = adjustKey(key, keySize)
# ans = keyExpansion(key)

