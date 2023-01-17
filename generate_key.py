import random
from textwrap import wrap

key_file = open('key.txt', 'w')

hex_numbers = wrap(''.join(random.choices('0123456789abcdef', k=64)), 2)
key_file.write(' '.join(hex_numbers[:16]) + '\n' + ' '.join(hex_numbers[16:]))
