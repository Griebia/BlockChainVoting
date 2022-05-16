import hashlib
import json
import sys
from collections import Counter
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import binascii
import requests
from flask import Flask, jsonify, request

import base58
from Crypto.PublicKey import RSA
from Crypto.Hash import RIPEMD160, SHA256
from Crypto.Signature import pkcs1_15


class Transaction:
    def __init__(self, sender_address: bytes, receiver_address: bytes, signature: str = ""):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.signature = signature

    def generate_data(self) -> bytes:
        transaction_data = self.generate_transaction_data(self.sender_address, self.receiver_address)
        return self.convert_transaction_data_to_bytes(transaction_data)

    def sign(self, private_key):
        transaction_data = self.generate_data()
        hash_object = SHA256.new(transaction_data)
        self.signature = pkcs1_15.new(private_key).sign(hash_object)
        return binascii.hexlify(self.signature).decode("utf-8")

    @staticmethod
    def generate_transaction_data(sender_address, receiver_address) -> dict:
        return {
            "receiver": receiver_address,
            "sender": sender_address,
        }

    @staticmethod
    def convert_transaction_data_to_bytes(transaction_data: dict):
        new_transaction_data = transaction_data.copy()
        new_transaction_data["receiver"] = str(transaction_data["receiver"])
        new_transaction_data["sender"] = str(transaction_data["sender"])
        print(json.dumps(new_transaction_data).replace(" ", ""))
        return json.dumps(new_transaction_data).replace(" ", "").encode('utf-8')

    @staticmethod
    def sign_data(data, private_key):
        hash_object = SHA256.new(data)
        signature = pkcs1_15.new(private_key).sign(hash_object)
        return binascii.hexlify(signature).decode("utf-8")
