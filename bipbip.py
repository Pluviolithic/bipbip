from bitstring import BitArray
import bitstring

bitstring.lsb0 = True

# permutations
P_1 = [1, 7, 6, 0, 2, 8, 12, 18, 19, 13, 14, 20, 21, 15, 16, 22, 23, 17, 9, 3, 4, 10, 11, 5]
P_2 = [0, 1, 4, 5, 8, 9, 2, 3, 6, 7, 10, 11, 16, 12, 13, 17, 20, 21, 15, 14, 18, 19, 22, 23]
P_3 = [16, 22, 11, 5, 2, 8, 0, 6, 19, 13, 12, 18, 14, 15, 1, 7, 21, 20, 4, 3, 17, 23, 10, 9]

def BipBipBox(x5, x4, x3, x2, x1, x0):
    x5 = int(x5, 2)
    x4 = int(x4, 2)
    x3 = int(x3, 2)
    x2 = int(x2, 2)
    x1 = int(x1, 2)
    x0 = int(x0, 2)
    return ''.join(map(str, [
        ((x4 & x3 & x2) | (x3 & x2 & x1) | (x5 & x0) | (x4 & x3) | (x3 & x2) | (x2 & x1) | x5),
        ((x1 & x2) | (x0 & x3) | x4 | (x1 & x4) | x5 | (x3 & x5)),
        ((x1 & x2) | x3 | (x0 & x3), x4 | (x2 & x4) | (x0 & x5)),
        (x2, (x1 & x3) | (x2 & x3) | (x0 & x4), x5 | (x4 & x5)),
        ((x5 & x3 & x2) | (x3 & x2 & x0) | (x5 & x3) | (x4 & x1) | (x3 & x2) | (x2 & x0) | x1),
        (x0 | (x0 & x2) | (x2 & x3) | x4 | (x1 & x5) | (x4 & x5))
    ]))

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
    

for i in range(1, 7):
    print(tweak_round_keys[i].bin)
