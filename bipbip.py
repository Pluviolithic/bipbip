from bitstring import BitArray
import bitstring

# allow indexing of the bitarrays from right to left
# i.e. least significant bit is at index 0
bitstring.lsb0 = True

# permutations
P_1 = [1, 7, 6, 0, 2, 8, 12, 18, 19, 13, 14, 20, 21, 15, 16, 22, 23, 17, 9, 3, 4, 10, 11, 5]
P_2 = [0, 1, 4, 5, 8, 9, 2, 3, 6, 7, 10, 11, 16, 12, 13, 17, 20, 21, 15, 14, 18, 19, 22, 23]
P_3 = [16, 22, 11, 5, 2, 8, 0, 6, 19, 13, 12, 18, 14, 15, 1, 7, 21, 20, 4, 3, 17, 23, 10, 9]

# Truth table entries for the S-box layer
Table_1 = "00  01  02  03  04  06  3e  3c  08  11  0e  17  2b  33  35  2d 19  1c  09  0c  15  13  3d  3b  31  2c  25  38  3a  26  36  2a 34  1d  37  1e  30  1a  0b  21  2e  1f  29  18  0f  3f  10  20 28  05  39  14  24  0a  0d  23  12  27  07  32  1b  2f  16  22"
Table_1 = Table_1.split()

# dictionary representation of the S-box truth table
sbox = {}
inverse_sbox = {}
for i in range(len(Table_1)):
    sbox[BitArray('0b' + bin(i)[2:].zfill(6)).bin] = BitArray('0x' + Table_1[i]).bin[2:]

# create inverted table for encryption
for key, entry in sbox.items():
    inverse_sbox[entry] = key
    
# would be done in parallel in hardware
# S-box layer
def BipBipBox(x5, x4, x3, x2, x1, x0):
    return BitArray('0b' + sbox[''.join(map(str, [int(x5), int(x4), int(x3), int(x2), int(x1), int(x0)]))])

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

# permutation layers  
def pi_1(x):
    y = BitArray(length=24)
    for i in range(24):
        y[i] = x[P_1[i]]
    return y
  
def pi_2(x):
    y = BitArray(length=24)
    for i in range(24):
        y[i] = x[P_2[i]]
    return y
  
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

# datapath rounds
def R(x):
    return pi_2(theta_d(pi_1(SBoxAll(x))))

def R_prime(x):
    return pi_3(SBoxAll(x))

# inverses to implement the encryption component

# S-box layer
def BipBipBox_inverse(x5, x4, x3, x2, x1, x0):
    return BitArray('0b' + inverse_sbox[''.join(map(str, [int(x5), int(x4), int(x3), int(x2), int(x1), int(x0)]))])

def SBoxAll_inverse(x):
    y = BitArray(length=24)
    for i in range(4):
        row = BipBipBox_inverse(x[6 * i + 5], x[6 * i + 4], x[6 * i + 3], x[6 * i + 2], x[6 * i + 1], x[6 * i])
        y[6 * i + 5] = row[5]
        y[6 * i + 4] = row[4]
        y[6 * i + 3] = row[3]
        y[6 * i + 2] = row[2]
        y[6 * i + 1] = row[1]
        y[6 * i] = row[0]
    return y

# permutation layer
def pi_1_inverse(x):
    y = BitArray(length=24)
    for i in range(24):
        y[P_1[i]] = x[i]
    return y

def pi_2_inverse(x):
    y = BitArray(length=24)
    for i in range(24):
        y[P_2[i]] = x[i]
    return y

def pi_3_inverse(x):
    y = BitArray(length=24)
    for i in range(24):
        y[P_3[i]] = x[i]
    return y

# mixing layer
def theta_d_inverse(x):
    y = BitArray(x)
    for i in range(24):
        y[i] = x[(i + 8) % 24] ^ x[(i + 20) % 24] ^ x[(i + 22) % 24]
    return y

# datapath rounds
def R_inverse(x):
    return SBoxAll_inverse(pi_1_inverse(theta_d_inverse(pi_2_inverse(x))))

def R_prime_inverse(x):
    return SBoxAll_inverse(pi_3_inverse(x))
    
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

# tweak schedule round functions
def G(a):
    return chi(pi_5(theta_t(pi_4(a))))
    
def G_prime(a):
    return chi(pi_5(theta_prime(pi_4(a))))

def generate_data_round_keys(T_star, tweak_round_keys):
    data_round_keys = []
    
    T_value = chi(T_star ^ tweak_round_keys[1])
    data_round_keys.append(E_0(T_value))
    data_round_keys.append(E_1(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[2])
    data_round_keys.append(E_0(T_value))
    data_round_keys.append(E_1(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[3])
    T_value = G_prime(T_value)
    data_round_keys.append(E_0(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[4])
    data_round_keys.append(E_0(T_value))
    T_value = G_prime(T_value)
    data_round_keys.append(E_0(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[5])
    data_round_keys.append(E_0(T_value))
    T_value = G_prime(T_value)
    data_round_keys.append(E_0(T_value))
    
    T_value = G(T_value ^ tweak_round_keys[6])
    data_round_keys.append(E_0(T_value))
    data_round_keys.append(E_1(T_value))
    
    return data_round_keys

# bipbip encryption implementation
def bipbip_enc(T_star, P, k0, tweak_round_keys):
    data_round_keys = generate_data_round_keys(T_star, tweak_round_keys)
    
    # three R' rounds
    R_value = R_prime_inverse(P ^ data_round_keys[10])
    R_value = R_prime_inverse(R_value ^ data_round_keys[9])
    R_value = R_prime_inverse(R_value ^ data_round_keys[8])
    
    # five R rounds
    R_value = R_inverse(R_value ^ data_round_keys[7])
    R_value = R_inverse(R_value ^ data_round_keys[6])
    R_value = R_inverse(R_value ^ data_round_keys[5])
    R_value = R_inverse(R_value ^ data_round_keys[4])
    R_value = R_inverse(R_value ^ data_round_keys[3])
    
    # three R' rounds
    R_value = R_prime_inverse(R_value ^ data_round_keys[2])
    R_value = R_prime_inverse(R_value ^ data_round_keys[1])
    R_value = R_prime_inverse(R_value ^ data_round_keys[0])
    
    return R_value ^ k0

# implementation of BipBip_(x, y, z) with BipBip_(3, 5, 3)
# x=3 shell rounds, y=5 core rounds, and z=3 more shell rounds
def bipbip_dec(T_star, C, k0, tweak_round_keys):
    data_round_keys = generate_data_round_keys(T_star, tweak_round_keys)
    
    # three R' rounds
    R_value = R_prime(C ^ k0)
    R_value = R_prime(R_value ^ data_round_keys[0])
    R_value = R_prime(R_value ^ data_round_keys[1])
    
    # five R rounds
    R_value = R(R_value ^ data_round_keys[2])
    R_value = R(R_value ^ data_round_keys[3])
    R_value = R(R_value ^ data_round_keys[4])
    R_value = R(R_value ^ data_round_keys[5])
    R_value = R(R_value ^ data_round_keys[6])

    # three R' rounds
    R_value = R_prime(R_value ^ data_round_keys[7])
    R_value = R_prime(R_value ^ data_round_keys[8])
    R_value = R_prime(R_value ^ data_round_keys[9])
    
    return R_value ^ data_round_keys[10]
    
def main():
    
    # read 256 bit hexadecimal key from file and convert to binary
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
        
    # random tweak; normally derived from the other 40 bits
    T = BitArray('0b0000101101110101100110101101111000111111')
    
    # extend the tweak to a length of 53 bits
    T_star = BitArray(T)
    T_star.append('0b1000000000000')
    
    # arbitrary plaintext
    P = BitArray('0b011010010101001001010100')
    
    print("Plaintext:  " + P.bin)
    C = bipbip_enc(T_star, P, k0, tweak_round_keys)  
    print("Ciphertext: " + C.bin)
    P = bipbip_dec(T_star, C, k0, tweak_round_keys)
    print("Plaintext:  " + P.bin)
        
if __name__ == "__main__":
    main()