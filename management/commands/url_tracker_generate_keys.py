# pylint: disable=no-member

import binascii
import json

from nacl.encoding import HexEncoder
from nacl.signing import SigningKey

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generates random signing and verification keys for API usage.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        signing_key = SigningKey.generate()

        print('SIGN: ' + signing_key.encode(encoder=HexEncoder).decode("ascii"))
        print('VERIFY: ' + signing_key.verify_key.encode(encoder=HexEncoder).decode("ascii"))
