# SAM-Chat is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# SAM-Chat is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with this
# program. If not, see <https://www.gnu.org/licenses/>.


import cryptography.exceptions
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

# Encryption

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA512(),
    length=32,
    salt=b'amougussexylovmao',
    iterations=100000,
    backend=default_backend()
)


def create_encryption(password: str):
    password = password.encode("utf-8", errors="ignore")
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return Fernet(key)




