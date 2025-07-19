import random, time
from sympy import nextprime
random.seed(42)

def inv_mod(a, prime):
    return pow(a, prime-2,prime) 

def tonneli_shanks(n, prime):
    if(pow(n,(prime-1)//2, prime) != 1):
        print("Not a square.")
        return
    
    if(prime%4 == 3):
        return pow(n, (prime+1)//4, prime)
    Q,S = prime-1, 0
    while(Q % 2 == 0): 
        Q//=2
        S+=1
    
    z = 2
    while(pow(z, (prime-1)//2, prime) != prime-1):
        z+=1

    c = pow(z, Q, prime)
    x = pow(n, (Q+1)//2, prime)
    t = pow(n , Q , prime) 
    M = S

    while(t % prime != 1): 
        i = 1
        check =  pow(t, 2, prime) 
        while check != 1:
            check = pow(check, 2, prime) 
            i += 1

        b = pow(c, 1 << (M-i-1), prime)
        x = (x * b) % prime
        t = ( t* b * b)% prime
        c = pow(b,2,prime)
        M = i
    return x 


def is_on_curve(P, a, b , prime):
    x, y = P
    return (y*y - (x*x*x + a*x + b))%prime == 0

def ec_add(P, Q, a, prime):
    if P is None: 
        return Q
    if Q is None: 
        return P
    x1, y1 = P 
    x2, y2 = Q
    if(x1 == x2 and (y1 + y2)%prime == 0):
        return None
    if(P != Q): 
        _d = ((y2-y1) * inv_mod(x2-x1, prime))%prime
    else:
        _d = ((3*x1*x1 + a) * inv_mod(2*y1, prime))%prime
    x3 = (_d*_d - x1 - x2) % prime
    y3 = (_d*(x1 - x3) - y1) % prime
    return (x3, y3)

def _scalarMul(k, P , a, prime):
    R = None
    Q = P
    while k > 0: 
        if k & 1:
            R = ec_add(R,Q,a,prime)
        Q = ec_add(Q,Q,a,prime)
        k >>= 1
    return R

def _setup(bitLen):
    P = nextprime(random.getrandbits(bitLen))
    while True: 
        a = random.randrange(P)
        b = random.randrange(P)
        if( 4* pow(a, 3, P) + 27* pow(b,2,P))%P != 0:
            break

    while True:
        x = random.randrange(P)
        check = (x*x*x + a*x + b)%P
        if pow(check, (P-1)//2, P) == 1: 
            y = tonneli_shanks(check, P)
            G = (x, y)
            break
    return P, a, b, G

def _Main(bitLen):
    P, a, b, G = _setup(bitLen)
    kA = random.randrange(1,P) 
    kB = random.randrange(1, P) 

    t0 = time.perf_counter()
    A = _scalarMul(kA, G, a, P) 
    t1= time.perf_counter() - t0

    t0 = time.perf_counter()
    B = _scalarMul(kB, G, a , P)
    t2 = time.perf_counter() - t0

    t0 = time.perf_counter()
    R = _scalarMul(kA, B, a, P)
    t3 = time.perf_counter() - t0

    print(R) 

    return t1,t2,t3

def _test(numOftrials = 5):
    
    for len in (128, 192, 256):
        time_A = 0
        time_B = 0
        time_R = 0
        for _ in range(numOftrials) : 
            _time = _Main(len)
            time_A += _time[0] 
            time_B += _time[1] 
            time_R += _time[2] 
        print(f"Len: {len}  A:{time_A/numOftrials :.3f}  B:{time_B/numOftrials :.3f}  R:{time_R/numOftrials :.3f}")



if __name__ == "__main__":
    _test()