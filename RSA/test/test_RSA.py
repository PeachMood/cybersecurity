from unittest import TestCase

import rsa
import rsa.core
from RSA import RSA

class TestRSA(TestCase):
    def test_small_data(self):
        print('--Функция шифрования--')
        e = 17
        d = 157
        n = 2773
        public_key = (e, n)
        private_key = (d, n)
        message = list('ITS ALL GREEK TO ME'.encode('utf-8'))
        print(f'Исходное сообщение: {message}', '\n')

        ciphertext = RSA.encrypt_decrypt(message, public_key)
        print(f'Зашифрованное сообщение: {ciphertext}')
        plaintext = RSA.encrypt_decrypt(ciphertext, private_key)
        print(f'Выходное сообщение: {plaintext}', '\n')

        ciphertext = [rsa.core.encrypt_int(number, e, n) for number in message]
        print(f'Зашифрованное сообщение: {ciphertext}')
        plaintext = [rsa.core.decrypt_int(number, d, n) for number in ciphertext]
        print(f'Выходное сообщение: {plaintext}', '\n\n')

    def test_medium_data(self):
        print('--Шифрование--')
        public_key, private_key = rsa.newkeys(1024)
        message = 'Really long example message'.encode('utf-8')
        print(f'Исходное сообщение: {message}', '\n')

        ciphertext = RSA.encrypt_message(message, (public_key.e, public_key.n))
        print(f'Зашифрованное сообщение: {ciphertext}')
        plaintext = RSA.decrypt_ciphertext(ciphertext, (private_key.d, private_key.n))
        print(f'Выходное сообщение: {plaintext}', '\n')

        ciphertext = rsa.encrypt(message, public_key)
        print(f'Зашифрованное сообщение: {ciphertext}')
        plaintext = rsa.decrypt(ciphertext, private_key)
        print(f'Выходное сообщение: {plaintext}', '\n\n')

    def test_large_data(self):
        print('--Электронная подпись--')
        public_key, private_key = RSA.generate_keys(1024)
        file_name = '1MB.bin'
        hash_method_name = 'BLAKE2b'
        signature = RSA.sign_file(file_name, private_key, hash_method_name)
        print(f'Электронная подпись: {signature}')
        verification_result = RSA.verify_signature(file_name, signature, public_key, hash_method_name)
        verification_result = 'пройдена' if verification_result else 'провалена'
        print('Верификация ' + verification_result, '\n\n')