
from Crypto.Cipher import ARC4


def arc4_encrypt(key, text):
    '''Encrypts a body of text using alleged-RC4 (Ron's Code 4) encryption.'''
    encryptor = ARC4.new(key)
    return encryptor.encrypt(text)

def arc4_decrypt(key, data):
    '''Decrypts a body of text from alleged-RC4 (Ron's Code 4) encrypted data.'''
    decryptor = ARC4.new(key)
    return decryptor.decrypt(data)

