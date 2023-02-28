import math
import random
import utils
import hashlib

class RSA:
    Key = (int, int)
    PublicKey = Key
    PrivateKey = Key

    HASH_METHODS = {
        'MD5': hashlib.md5,
        'SHA3-256': hashlib.sha3_256,
        'SHA3-512': hashlib.sha3_512,
        'BLAKE2b': hashlib.blake2b,
        'BLAKE2s': hashlib.blake2s,
    }

    @classmethod
    def generate_keys(cls, length: int) -> (PublicKey, PrivateKey):
        p = utils.generate_prime_number(length // 2)
        q = utils.generate_prime_number(length // 2)
        while p == q:
            q = utils.generate_prime_number(length // 2)

        n = p * q
        phi_n = (p - 1) * (q - 1)
        e = random.randint(2, phi_n - 1)

        while math.gcd(e, phi_n) != 1:
            e = random.randint(2, phi_n - 1)

        d = utils.multiplicative_inverse(e, phi_n)
        return (d, n), (e, n)

    @classmethod
    def encrypt_decrypt(cls, numbers: list[int], key: Key) -> list[int]:
        power, module = key
        output = []
        for number in numbers:
            number = utils.module_power(number, power, module)
            output.append(number)
        return output

    @classmethod
    def encrypt_message(cls, message: bytes, public_key: PublicKey) -> bytes:
        e, n = public_key

        block_length = (n.bit_length() - 1) // 8
        blocks = utils.bytes_to_blocks(message, block_length)
        ciphertext = cls.encrypt_decrypt(blocks, public_key)

        return utils.blocks_to_bytes(ciphertext)

    @classmethod
    def decrypt_ciphertext(cls, ciphertext: bytes, private_key: PublicKey) -> bytes:
        d, n = private_key

        block_length = ((n.bit_length() - 1) // 8) + 1
        blocks = utils.bytes_to_blocks(ciphertext, block_length)
        message = cls.encrypt_decrypt(blocks, private_key)

        return utils.blocks_to_bytes(message)

    @classmethod
    def hash_file(cls, file_name: str, hash_method_name: any) -> bytes:
        hash_method = cls.HASH_METHODS[hash_method_name]
        hasher = hash_method()
        with open(file_name, "rb") as file:
            while True:
                data = file.read(hasher.block_size)
                hasher.update(bytes(data))
                if not data:
                    break
        return hasher.digest()

    @classmethod
    def sign_file(cls, file_name: str, private_key: PrivateKey, hash_method_name: str) -> bytes:
        hash = cls.hash_file(file_name, hash_method_name)
        return cls.encrypt_message(hash, private_key)

    @classmethod
    def verify_signature(cls, file_name: str, signature: bytes, public_key: PublicKey, hash_method_name: str) -> bool:
        hash = cls.hash_file(file_name, hash_method_name)
        decrypt = cls.decrypt_ciphertext(signature, public_key)
        return hash == decrypt

