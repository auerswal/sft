#! /usr/bin/env python3

# thotp.py - generate HOTP or TOTP one-time password (a.k.a. verification code)
# Copyright (C) 2023-2025  Erik Auerswald <auerswal@unix-ag.uni-kl.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Generate a one-time password using the HOTP or TOTP algorithm.

This script reads a shared secret key, and uses either the current time
(for TOTP) or a given count (for HOTP) to compute a code intended for
use as a one-time password.  HOTP or TOTP are often used as an additional
authentication factor in 2FA resp. MFA schemes.  TOTP uses HOTP, but
computes the "count" from the current time instead of counting the number
of already used passwords.

HMAC is specified in RFC 2104.
HOTP is specified in RFC 4226.
TOTP is specified in RFC 6238.
"""

import argparse
import base64
import hmac
import math
import sys
import time

PROG = 'thotp.py'
VERS = '0.5.1'
COPY = 'Copyright (C) 2023-2025  Erik Auerswald <auerswal@unix-ag.uni-kl.de>'
LICE = '''\
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
'''
DESC = '''\
Compute a one-time password using either the HOTP (see RFC 4226) or the
TOTP (see RFC 6238) algorithm.

The HOTP algorithm is selected by providing a counter value.  Without a
counter value, the TOTP algorithm is used.  TOTP computes a time-based
counter value, and then invokes HOTP with this counter.

The shared secret keys used for two-factor or multi-factor authentication
are often encoded for transfer, e.g., using Base32.

OTP parameters are often conveyed using a URI encoded as a QR code.  The
URI uses the "otpauth" scheme provisionally registered with IANA:

    otpauth://TYPE/LABEL?PARAMETERS

 - The type is either hotp or totp.
 - The label identifys the associated account.
 - The following parameters can be used:
    - secret: Base32 encoded shared secret key (required)
    - issuer: string indicating the associated service (recommended)
    - algorithm: SHA1 (default), SHA256, or SHA512 (optional)
    - digits: 6 (default), 7, or 8 (optional)
    - period: time-step duration in seconds, default 30 (optional, TOTP only)
    - counter: initial counter value for HOTP (required, HOTP only)
'''
EPIL = f'''\
Examples:

    # compute TOTP code from GPG-encrypted raw shared secret key
    $ gpg --decrypt --quiet ~/.totp-secret | {PROG}

    # compute TOTP code as above and copy it to the X Window System clipboard
    $ gpg --decrypt --quiet ~/.totp-secret | {PROG} -n | xclip
'''
KEY_ENCODINGS = ['hex', 'base16', 'base32', 'base64']


def cmd_line_args():
    """Parse command line arguments."""
    cmd_line = argparse.ArgumentParser(
        prog=PROG, description=DESC, epilog=EPIL,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    cmd_line.add_argument('-V', '--version', action='version',
                          version='\n'.join([PROG + ' ' + VERS, COPY, LICE]))
    cmd_line.add_argument('-f', '--file', default='/dev/stdin',
                          help='read shared secret key from file ' +
                               '(default: /dev/stdin)')
    cmd_line.add_argument('-c', '--counter', type=int,
                          help='counter value for HOTP algorithm')
    cmd_line.add_argument('-e', '--key-encoding', choices=KEY_ENCODINGS,
                          help='provided secret key is encoded')
    cmd_line.add_argument('-b', '--base32', dest='key_encoding',
                          action='store_const', const='base32',
                          help='provided secret key is Base32 encoded')
    cmd_line.add_argument('-s', '--time-step-size', type=int, default=30,
                          help='TOTP time-step duration in seconds ' +
                               '(default: 30)')
    cmd_line.add_argument('-H', '--hash',
                          choices=['sha1', 'sha256', 'sha512'],
                          default='sha1',
                          help='select hash algorithm (default: sha1)')
    cmd_line.add_argument('-d', '--digits', type=int, default=6,
                          help='number of digits in one-time password ' +
                               '(default: 6)')
    cmd_line.add_argument('-n', '--no-newline', action='store_true',
                          help='omit end-of-line sequence from output')
    return cmd_line.parse_args()


def warn(msg):
    """Print message with warning prefix to standard error."""
    print(f'{PROG}: WARNING:', msg, file=sys.stderr)


def err(msg):
    """Print message with error prefix to standard error."""
    print(f'{PROG}: ERROR:', msg, file=sys.stderr)


def valid_settings(settings):
    """Check for acceptable option values not guaranteed by argparse."""
    if settings.time_step_size <= 0:
        err('time-step duration must be greater than 0')
        return False
    if settings.digits <= 0:
        err('number of digits must be greater than 0')
        return False
    if settings.digits > 11:
        err('number of digits must be less than 12')
        return False
    if (settings.key_encoding is not None and
            settings.key_encoding not in KEY_ENCODINGS):
        err(f'unsupported key encoding "{settings.key_encoding}"')
        return False
    if settings.digits < 6:
        warn('using less than 6 digits does not conform to RFC 4226')
    return True


def read_secret_key(file_name):
    """Read the shared secret key from a file."""
    key = b''
    with open(file_name, mode='rb') as key_file:
        while buf := key_file.read():
            key += buf
    key = key.strip()
    return key


def decode_key(key, encoding):
    """Decode an encoded shared secret key."""
    try:
        if encoding is None:
            return key
        elif encoding == 'hex' or encoding == 'base16':
            return base64.b16decode(key)
        elif encoding == 'base32':
            return base64.b32decode(key)
        elif encoding == 'base64':
            return base64.b64decode(key)
        else:
            err(f'unknown key encoding "{encoding}"')
            return None
    except base64.binascii.Error as exc:
        err(f'cannot decode secret key: {exc}')
        return None


def totp_counter(current_time, time_step_size):
    """Compute HOTP counter value from time and time step duration.

    >>> # Test values from RFC 6238 Appendix B:
    >>> totp_counter(59, 30).to_bytes(length=8, byteorder='big').hex()
    '0000000000000001'
    >>> totp_counter(1111111109, 30).to_bytes(length=8, byteorder='big').hex()
    '00000000023523ec'
    >>> totp_counter(1111111111, 30).to_bytes(length=8, byteorder='big').hex()
    '00000000023523ed'
    >>> totp_counter(1234567890, 30).to_bytes(length=8, byteorder='big').hex()
    '000000000273ef07'
    >>> totp_counter(2000000000, 30).to_bytes(length=8, byteorder='big').hex()
    '0000000003f940aa'
    >>> totp_counter(20000000000, 30).to_bytes(length=8, byteorder='big').hex()
    '0000000027bc86aa'
    """
    return math.floor(current_time / time_step_size)


def set_counter(value, time_step_size):
    """Ensure the counter required for HOTP has a value.

    If a value has been given via command line option, retain it.
    Otherwise, compute the TOTP counter value based on the current Unix time
    and the time step duration.
    """
    if value is None:
        value = totp_counter(time.time(), time_step_size)
    return value


def compute_hmac(key, counter, hash_algo):
    """Compute HMAC(key, counter) using selected hash algorithm.

    >>> # Test values from RFC 4226 Appendix D:
    >>> secret = b'12345678901234567890'
    >>> compute_hmac(secret, 0, 'sha1').hex()
    'cc93cf18508d94934c64b65d8ba7667fb7cde4b0'
    >>> compute_hmac(secret, 1, 'sha1').hex()
    '75a48a19d4cbe100644e8ac1397eea747a2d33ab'
    >>> compute_hmac(secret, 2, 'sha1').hex()
    '0bacb7fa082fef30782211938bc1c5e70416ff44'
    >>> compute_hmac(secret, 3, 'sha1').hex()
    '66c28227d03a2d5529262ff016a1e6ef76557ece'
    >>> compute_hmac(secret, 4, 'sha1').hex()
    'a904c900a64b35909874b33e61c5938a8e15ed1c'
    >>> compute_hmac(secret, 5, 'sha1').hex()
    'a37e783d7b7233c083d4f62926c7a25f238d0316'
    >>> compute_hmac(secret, 6, 'sha1').hex()
    'bc9cd28561042c83f219324d3c607256c03272ae'
    >>> compute_hmac(secret, 7, 'sha1').hex()
    'a4fb960c0bc06e1eabb804e5b397cdc4b45596fa'
    >>> compute_hmac(secret, 8, 'sha1').hex()
    '1b3c89f65e6c9e883012052823443f048b4332db'
    >>> compute_hmac(secret, 9, 'sha1').hex()
    '1637409809a679dc698207310c8c7fc07290d9e5'
    """
    counter = counter.to_bytes(length=8, byteorder='big')
    return hmac.digest(key, counter, hash_algo)


def hotp_extract_bytes(hmac_value):
    """Extract 4-byte sequence from HMAC result.

    >>> # Test values from RFC 4226 Appendix D:
    >>> hmac_value = bytes.fromhex('cc93cf18508d94934c64b65d8ba7667fb7cde4b0')
    >>> hotp_extract_bytes(hmac_value).hex()
    '4c93cf18'
    >>> hmac_value = bytes.fromhex('75a48a19d4cbe100644e8ac1397eea747a2d33ab')
    >>> hotp_extract_bytes(hmac_value).hex()
    '41397eea'
    >>> hmac_value = bytes.fromhex('0bacb7fa082fef30782211938bc1c5e70416ff44')
    >>> hotp_extract_bytes(hmac_value).hex()
    '082fef30'
    >>> hmac_value = bytes.fromhex('66c28227d03a2d5529262ff016a1e6ef76557ece')
    >>> hotp_extract_bytes(hmac_value).hex()
    '66ef7655'
    >>> hmac_value = bytes.fromhex('a904c900a64b35909874b33e61c5938a8e15ed1c')
    >>> hotp_extract_bytes(hmac_value).hex()
    '61c5938a'
    >>> hmac_value = bytes.fromhex('a37e783d7b7233c083d4f62926c7a25f238d0316')
    >>> hotp_extract_bytes(hmac_value).hex()
    '33c083d4'
    >>> hmac_value = bytes.fromhex('bc9cd28561042c83f219324d3c607256c03272ae')
    >>> hotp_extract_bytes(hmac_value).hex()
    '7256c032'
    >>> hmac_value = bytes.fromhex('a4fb960c0bc06e1eabb804e5b397cdc4b45596fa')
    >>> hotp_extract_bytes(hmac_value).hex()
    '04e5b397'
    >>> hmac_value = bytes.fromhex('1b3c89f65e6c9e883012052823443f048b4332db')
    >>> hotp_extract_bytes(hmac_value).hex()
    '2823443f'
    >>> hmac_value = bytes.fromhex('1637409809a679dc698207310c8c7fc07290d9e5')
    >>> hotp_extract_bytes(hmac_value).hex()
    '2679dc69'
    """
    offset = int(hmac_value[-1] & 0xf)
    bin_code = (((hmac_value[offset] & 0x7f) << 24) |
                (hmac_value[offset + 1] << 16) |
                (hmac_value[offset + 2] << 8) |
                (hmac_value[offset + 3]))
    return bin_code.to_bytes(length=4, byteorder='big')


def hotp_bytes_to_int(extracted):
    """Interpret 4-byte sequence as big-endian integer.

    >>> # Test values from RFC 4226 Appendix D:
    >>> hotp_bytes_to_int(bytes.fromhex('4c93cf18'))
    1284755224
    >>> hotp_bytes_to_int(bytes.fromhex('41397eea'))
    1094287082
    >>> hotp_bytes_to_int(bytes.fromhex('082fef30'))
    137359152
    >>> hotp_bytes_to_int(bytes.fromhex('66ef7655'))
    1726969429
    >>> hotp_bytes_to_int(bytes.fromhex('61c5938a'))
    1640338314
    >>> hotp_bytes_to_int(bytes.fromhex('33c083d4'))
    868254676
    >>> hotp_bytes_to_int(bytes.fromhex('7256c032'))
    1918287922
    >>> hotp_bytes_to_int(bytes.fromhex('04e5b397'))
    82162583
    >>> hotp_bytes_to_int(bytes.fromhex('2823443f'))
    673399871
    >>> hotp_bytes_to_int(bytes.fromhex('2679dc69'))
    645520489
    """
    return int.from_bytes(extracted, byteorder='big')


def hotp_code(extracted_value, digits):
    """Generate N-digit number from extracted 4-byte integer.

    >>> # Test values from RFC 4226 Appendix D:
    >>> hotp_code(1284755224, 6)
    '755224'
    >>> hotp_code(1094287082, 6)
    '287082'
    >>> hotp_code(137359152, 6)
    '359152'
    >>> hotp_code(1726969429, 6)
    '969429'
    >>> hotp_code(1640338314, 6)
    '338314'
    >>> hotp_code(868254676, 6)
    '254676'
    >>> hotp_code(1918287922, 6)
    '287922'
    >>> hotp_code(82162583, 6)
    '162583'
    >>> hotp_code(673399871, 6)
    '399871'
    >>> hotp_code(645520489, 6)
    '520489'
    """
    code = extracted_value % (10**digits)
    return str(code).rjust(digits, '0')


def hotp_generate_code(hmac_value, digits):
    """Generate N-digit HOTP code from an HMAC result."""
    extracted_bytes = hotp_extract_bytes(hmac_value)
    extracted_int = hotp_bytes_to_int(extracted_bytes)
    code = hotp_code(extracted_int, digits)
    return code


def compute_hotp_code(secret_key, counter_value, hash_algorithm, digits):
    """Compute HOTP code.

    >>> # Test values from RFC 6238 Appendix B:
    >>> key_sha1 = b'12345678901234567890'
    >>> key_sha256 = b'12345678901234567890123456789012'
    >>> key_sha512 = \
        b'1234567890123456789012345678901234567890123456789012345678901234'
    >>> compute_hotp_code(key_sha1, 0x0000000000000001, 'sha1', 8)
    '94287082'
    >>> compute_hotp_code(key_sha256, 0x0000000000000001, 'sha256', 8)
    '46119246'
    >>> compute_hotp_code(key_sha512, 0x0000000000000001, 'sha512', 8)
    '90693936'
    >>> compute_hotp_code(key_sha1, 0x00000000023523EC, 'sha1', 8)
    '07081804'
    >>> compute_hotp_code(key_sha256, 0x00000000023523EC, 'sha256', 8)
    '68084774'
    >>> compute_hotp_code(key_sha512, 0x00000000023523EC, 'sha512', 8)
    '25091201'
    >>> compute_hotp_code(key_sha1, 0x00000000023523ED, 'sha1', 8)
    '14050471'
    >>> compute_hotp_code(key_sha256, 0x00000000023523ED, 'sha256', 8)
    '67062674'
    >>> compute_hotp_code(key_sha512, 0x00000000023523ED, 'sha512', 8)
    '99943326'
    >>> compute_hotp_code(key_sha1, 0x000000000273EF07, 'sha1', 8)
    '89005924'
    >>> compute_hotp_code(key_sha256, 0x000000000273EF07, 'sha256', 8)
    '91819424'
    >>> compute_hotp_code(key_sha512, 0x000000000273EF07, 'sha512', 8)
    '93441116'
    >>> compute_hotp_code(key_sha1, 0x0000000003F940AA, 'sha1', 8)
    '69279037'
    >>> compute_hotp_code(key_sha256, 0x0000000003F940AA, 'sha256', 8)
    '90698825'
    >>> compute_hotp_code(key_sha512, 0x0000000003F940AA, 'sha512', 8)
    '38618901'
    >>> compute_hotp_code(key_sha1, 0x0000000027BC86AA, 'sha1', 8)
    '65353130'
    >>> compute_hotp_code(key_sha256, 0x0000000027BC86AA, 'sha256', 8)
    '77737706'
    >>> compute_hotp_code(key_sha512, 0x0000000027BC86AA, 'sha512', 8)
    '47863826'
    """
    hmac_value = compute_hmac(secret_key, counter_value, hash_algorithm)
    hotp_code = hotp_generate_code(hmac_value, digits)
    return hotp_code


def main():
    """Script entry point."""
    if not valid_settings(ARGS):
        return 1
    key = read_secret_key(ARGS.file)
    key = decode_key(key, ARGS.key_encoding)
    if not key:
        err('cannot read secret key')
        return 1
    counter = set_counter(ARGS.counter, ARGS.time_step_size)
    hotp_value = compute_hotp_code(key, counter, ARGS.hash, ARGS.digits)
    print(hotp_value, end='' if ARGS.no_newline else '\n')
    return 0


if __name__ == '__main__':
    ARGS = cmd_line_args()
    sys.exit(main())

# vim:tabstop=4:shiftwidth=4:expandtab:
