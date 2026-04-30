import base64
import hashlib
import os


def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(40)).decode().rstrip("=")


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")