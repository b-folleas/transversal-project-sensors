# microbit-module: rsa@0.1.0

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
