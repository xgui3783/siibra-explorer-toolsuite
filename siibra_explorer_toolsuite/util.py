import math
import struct

cipher = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-'
separator = '.'
neg = '~'
def encode_number(n, float_flag=False):
    if float_flag:
        b=struct.pack('f', n)
        new_n=struct.unpack('i',b)
        return encode_int(new_n[0])
    else:
        return encode_int(n)

def encode_int(n):
    if not isinstance(n, int):
        raise ValueError('Cannot encode int')

    residual=None
    result=''
    if n < 0:
        result += neg
        residual = n * -1
    else:
        residual = n
    
    while True:
        result = cipher[residual % 64] + result
        residual = math.floor(residual / 64)

        if residual == 0:
            break
    return result