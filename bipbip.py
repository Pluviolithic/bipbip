from bitstring import BitArray
import bitstring

bitstring.lsb0 = True

# permutations
P_1 = [1, 7, 6, 0, 2, 8, 12, 18, 19, 13, 14, 20, 21, 15, 16, 22, 23, 17, 9, 3, 4, 10, 11, 5]
P_2 = [0, 1, 4, 5, 8, 9, 2, 3, 6, 7, 10, 11, 16, 12, 13, 17, 20, 21, 15, 14, 18, 19, 22, 23]
P_3 = [16, 22, 11, 5, 2, 8, 0, 6, 19, 13, 12, 18, 14, 15, 1, 7, 21, 20, 4, 3, 17, 23, 10, 9]

def BipBipBox(x5, x4, x3, x2, x1, x0):
    x5 = int(x5)
    x4 = int(x4)
    x3 = int(x3)
    x2 = int(x2)
    x1 = int(x1)
    x0 = int(x0)
    return BitArray('0b' + ''.join(map(str, [
        ((x4 & x3 & ~x2) | (~x3 & x2 & x1) | (x5 & ~x0) | (x3 & x2)),
        ((x1 & x2) | (x0 & x3) | (~x1 & x4) | (~x3 & x5)),
        ((x1 & x2) | (~x0 & x3) | (~x2 & x4) | (x0 & x5)),
        ((x1 & x3) | (x2 & ~x3) | (x0 & x4) | (~x4 & x5)),
        ((x5 & x3 & ~x2) | (~x3 & x2 & x0) | (~x4 & x1) | (x3 & x2)),
        ((x0 & ~x2) | (x2 & x3) | (x1 & x5) | (x4 & ~x5))
    ])))
  
# would be done in parallel in hardware  
def SBoxAll(x):
    y = BitArray(length=24)
    for i in range(4):
        row = BipBipBox(x[6 * i + 5], x[6 * i + 4], x[6 * i + 3], x[6 * i + 2], x[6 * i + 1], x[6 * i])
        y[6 * i + 5] = row[5]
        y[6 * i + 4] = row[4]
        y[6 * i + 3] = row[3]
        y[6 * i + 2] = row[2]
        y[6 * i + 1] = row[1]
        y[6 * i] = row[0]
    return y

# mixing layer
def theta_d(x):
    y = BitArray(length=24)
    for i in range(24):
        y[i] = x[i] ^ x[(i + 2) % 24] ^ x[(i + 12) % 24]
    return y

# linear mixing layers
def theta_t(a):
    new_a = BitArray(length=53)
    for i in range(53):
        new_a[i] = a[i] ^ a[(i + 1) % 53] ^ a[(i + 8) % 53]
    return new_a

def theta_prime(a):
    new_a = BitArray(length=53)
    for i in range(52):
        new_a[i] = a[i + 1]
    new_a[52] = a[52]
    return new_a

# permutation layer   
def pi_1(x):
    y = BitArray(length=24)
    for i in range(24):
        y[i] = x[P_1[i]]
    return y

# permutation layer     
def pi_2(x):
    y = BitArray(length=24)
    for i in range(24):
        y[i] = x[P_2[i]]
    return y
  
# permutation layer      
def pi_3(x):
    y = BitArray(length=24)
    for i in range(24):
        y[i] = x[P_3[i]]
    return y

# bit permutations
def pi_4(a):
    new_a = BitArray(length=53)
    for i in range(53):
        new_a[i] = a[(13 * i) % 53]
    return new_a
    
def pi_5(a):
    new_a = BitArray(length=53)
    for i in range(53):
        new_a[i] = a[(11 * i) % 53]
    return new_a

# non-linear layer
def chi(a):
    new_a = BitArray(length=53)
    for i in range(53):
        new_a[i] = a[i] ^ (a[(i + 1) % 53] ^ 1) & a[(i + 2) % 53]
    return new_a
    
# data-round key extractors
def E_0(xi):
    ki = BitArray(length=24)
    for i in range(24):
        ki[i] = xi[2 * i]
    return ki

def E_1(xi):
    ki = BitArray(length=24)
    for i in range(24):
        ki[i] = xi[2 * i + 1]
    return ki

# datapath rounds
def R(x):
    return pi_2(theta_d(pi_1(SBoxAll(x))))

def R_prime(x):
    return pi_3(SBoxAll(x))

# tweak schedule round functions
def G(a):
    return chi(pi_5(theta_t(pi_4(a))))
    
def G_prime(a):
    return chi(pi_5(theta_prime(pi_4(a))))

def bipbip(T_star, C, k0, tweak_round_keys):
    R_value = R_prime(C ^ k0)
    
    T_value = chi(T_star ^ tweak_round_keys[1])
    
    R_value = R_prime(R_value ^ E_0(T_value))
    R_value = R_prime(R_value ^ E_1(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[2])
    
    R_value = R(R_value ^ E_0(T_value))
    R_value = R(R_value ^ E_1(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[3])
    T_value = G_prime(T_value)
    
    R_value = R(R_value ^ E_0(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[4])
    
    R_value = R(R_value ^ E_0(T_value))
    
    T_value = G_prime(T_value)
    
    R_value = R(R_value ^ E_0(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[5])
    
    R_value = R_prime(R_value ^ E_0(T_value))
    
    T_value = G_prime(T_value)
    
    R_value = R_prime(R_value ^ E_0(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[6])
    
    R_value = R_prime(R_value ^ E_0(T_value))
    
    return R_value ^ E_1(T_value)
    
def main():
    key_hex_values = open('key.txt').read().split()
    key_binary_values = [ bin(int(x, 16))[2:].zfill(8) for x in key_hex_values]

    K = BitArray('0b' + ''.join(key_binary_values))

    # one 24-bit data-round key k^0
    k0 = BitArray(length=24)
    for i in range(1, 25):
        k0[i - 1] = K[(3 ** i) % 256]

    # six 53-bit tweak round keys
    tweak_round_keys = {}
    for i in range(1, 7):
        tweak_round_keys[i] = BitArray('0b' + ''.join(map(str, [
            K.bin[(53 * i + x) % 256] for x in range(53)
        ])))
        
    # random tweak for now
    T = BitArray('0b0000101101110101100110101101111000111111')
    T_star = BitArray(T)
    T_star.append('0b1000000000000')
    C = BitArray('0b011010010101001001010100')
    
    print(C.bin)
    P = bipbip(T_star, C, k0, tweak_round_keys)  
    print(P.bin)
    C = bipbip(T_star, P, k0, tweak_round_keys)
    print(C.bin)
        
if __name__ == "__main__":
    main()