import numpy as np

def isprime(n):
    """return True if n is prime, False if not
    n must be an int"""

    if n == 1 or n == 2:
        return True

    if n % 2 == 0:
        return False

    r = n**0.5

    if r == int(r):
        return False

    for x in range(3, int(r), 2):
        if n % x == 0:
            return False

    return True

def coupcoup(k, long):
    """"cut long blocks in a string k and return a list of blocks"""

    d, f = 0, long
    l = []

    while f <= len(k):
        l.append(k[d:f])
        d, f = f, f + long
    m = len(k) % long

    if m != 0:
        l.append(k[len(k)-m:])

    return l


def pgcd(a, b):
    """euclidic algorithm
    Input: int a, b
    Output: a as pgcd"""

    # euclidic algorithm
    while (b > 0):
        r = a % b
        a, b = b, r
    return a


def pgcde(a, b):
    """extended euclidic algorithm with bezout coefficient u and v
    Input: int a, b
    Output: r = pgcd(a,b) and u, v int as a*u + b*v = r
    """
    r, u, v = a, 1, 0
    rp, up, vp = b, 0, 1

    while rp != 0:
        q = r//rp
        rs, us, vs = r, u, v
        r, u, v = rp, up, vp
        rp, up, vp = (rs - q*rp), (us - q*up), (vs - q*vp)

    return (r, u, v)


def key():
    """return dict with private and public key as tuples : {priv:(private key),pub:(public key)}"""

    # random prime int choice (p and q)
    p = np.random.choice(1000, 1)
    q = np.random.choice(1000, 1)

    while isprime(p) is False:
        p = np.random.choice(1000, 1)

    while isprime(q) is False:
        q = np.random.choice(1000, 1)

    # calculating n and m
    n = p*q
    m = (p-1)*(q-1)

    # search for c of m as pgcd(m,c)=1 and d as d = pgcde(m,c) with 2 < d < m
    r = 10
    d = 0
    while r != 1 or d <= 2 or d >= m:
        c = np.random.choice(1000, 1)
        r, d, v = pgcde(c, m)

    n, c, d = int(n), int(c), int(d)

    return {"priv": (n, c), "pub": (n, d)}


def encrypt(n, c, msg):

    # converting message to ascii
    asc = [str(ord(j)) for j in msg]

    # add 0 to have a fixed length (3) of each ascii code
    for i, k in enumerate(asc):
        if len(k) < 3:
            while len(k) < 3:
                k = '0' + k
            asc[i] = k

    # creating blocs with size < n (here blocs of 4)
    ascg = ''.join(asc)
    d, f = 0, 4

    while len(ascg) % f != 0:  # we had 0 at the end of ascg so that len(ascg) is a multiple of f 
        ascg = ascg + '0'
    l = []

    while f <= len(ascg):
        l.append(ascg[d:f])
        d, f = f, f + 4

    # chiffrement des groupes
    crypt = [str(((int(i))**c) % n) for i in l]
    return crypt


def decrypt(n, d, *crypt):
    """*crypt is list of blocs"""

    # decrypting blocs
    result = [str((int(i)**d) % n) for i in crypt[0]]

    # we add 0 at the beginning of blocs to create bloc of 4
    for i, s in enumerate(result):
        if len(s) < 4:
            while len(s) < 4:
                s = '0' + s
            result[i] = s

    # we create group of 3 and convert into ascii
    g = ''.join(result)
    asci = ''
    d, f = 0, 3
    while f < len(g):
        asci = asci + chr(int(g[d:f]))  # convert to ascii
        d, f = f, f + 3
    return asci


if __name__ == '__main__':

    msg = "F/1,1,1/2,2,2/3,3,3/4,4,4/6,6,6&I/1,1,1/2,2,2/3,3,3/4,4,4/6,6,6"

    key = key() # key = {priv:(n,c),pub:(n, d)}
    # print(key)
    private_key = key['priv']
    public_key = key['pub']
    print(private_key)
    print(public_key)

    print('Chiffrement avec clé public, déchiffrement avec clé privé')
    crypted_msg = encrypt(public_key[0],public_key[1], msg)
    # print(crypted_msg)
    decrypt_msg = decrypt(private_key[0],private_key[1],crypted_msg)
    print(decrypt_msg)
    
    print('Chiffrement avec clé privé, déchiffrement avec clé public')
    crypted_msg = encrypt(private_key[0],private_key[1], msg)
    # print(crypted_msg)
    decrypt_msg = decrypt(public_key[0],public_key[1],crypted_msg)
    print(decrypt_msg)
    