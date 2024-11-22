'''
#!/usr/bin/python
'''
#import os
import sys
import argparse
import hashlib
import hmac
import string
import time
import subprocess
import oathtool
#import base64
#import requests
from cryptography.fernet import Fernet



'''
k is the key.  The server must share this key or the method for deriving 
this key with the client

c is an 8-byte counter value, it increments after each OTP generation.
Therefore the counter must be sync'd with client and server

Client: the HOTP generator
Server: the HITP validator
'''
def	check_hex_character(key):
	if len(key) != 64:
	#checks if length is 64 and if the string represents hexidecimal characters
#		print("./ft_otp: error: key must be 64 hexadecimal characters.")
		print(f"Error: Provided key has {len(key)} characters, but 64 are required.")
		sys.exit(1)
	if not all(c in string.hexdigits for c in key):
		print("./ft_otp: error: key must contain only hexadecimal characters.")
		sys.exit(1)

def	make_encrypted_key(key):
	try:
		key_bytes = bytes.fromhex(key)
		#converts 64-char hex string to 32 bytes binary format
		encryption_key = Fernet.generate_key()
		cipher = Fernet(encryption_key)
		encrypted_key = cipher.encrypt(key_bytes)
		with open('ft_otp.key', 'wb') as f:
		#opens file in binary mode
			f.write(encrypted_key)
		with open('ft_otp.fernet', 'wb') as fernet_file:
			fernet_file.write(encryption_key)
		print("Key was successfully encrypted and stored in ft_otp.key")
	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)

'''
Generage an OTP using the HOTP algorithm and a time-based counter
pulled the information from RFC 4226
'''
def	generate_otp(hmac_key):
	try:
		with open(hmac_key, "rb") as key_file:
			encrypted_key = key_file.read()
		with open('ft_otp.fernet', "rb") as fernet_file:
			encryption_key = fernet_file.read()
		cipher = Fernet(encryption_key)
		key_bytes = cipher.decrypt(encrypted_key)
		counter = int(time.time() // 30)
		counter_bytes = counter.to_bytes(8, byteorder='big')
		#8 byte big endian
		hmac_hash = hmac.new(key_bytes, counter_bytes, hashlib.sha1).digest()
		#.digets returns the binary representation
		#.hexdigets returns a hexadecimal string representation of the hash
		offset = hmac_hash[19] & 0xf
		#extract the 19th byte, mask to get the lower/last 4 bits
		#integer; the first byte is masked with a 0x7f.
		bin_code = ((hmac_hash[offset] & 0x7f) << 24 |
			(hmac_hash[offset + 1] & 0xff) << 16 |
			(hmac_hash[offset + 2] & 0xff) << 8 |
			(hmac_hash[offset + 3] & 0xff))
		# Only use the lower 31 bits of the result, this builds the 31-bit binary code
		#We treat the dynamic binary code as a 31-bit, unsigned, big-endian
		otp = bin_code % (10 ** 6) #or % 1,000,000
		#generate the OTP (6 digits)
		print(f"Generated OTP: {otp:06}")
		#zero pad to ensure 6 digits
		command = [
			"oathtool",
			"-c", str(counter),
			key_bytes.hex()
		]
		print(f"Running command: {' '.join(command)}")
		result = subprocess.run(command, capture_output=True, text=True, check=True)
		oathtool_otp = result.stdout.strip()

		print(f"OATHTool OTP: {oathtool_otp}")
		print(f"Match: {'Yes' if oathtool_otp == f'{otp:06}' else 'No'}")		
		return otp
	except FileNotFoundError:
		print(f"Error: File {hmac_key} not found.")
		sys.exit(1)
	except subprocess.CalledProcessError as e:
		print(f"Error running oathtool: {e.stderr.strip()}")
		sys.exit(1)
	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)


		
def main():
	# Initialize argparse to parse arguments in the terminal
	parser = argparse.ArgumentParser(description="Generates new temporary passwords")
	parser.add_argument("-g", type=str, help="Encrypts and stores key in ft_otp.key")
	parser.add_argument("-k", type=str, help="Generate a new temporary password")
	args = parser.parse_args()

	if args.g:
		try:
			with open(args.g, "r") as f:
				key = f.read().strip()
				#removes any surrounding white space
				check_hex_character(key)
				make_encrypted_key(key)
		except FileNotFoundError:
			print(f"Error: File {args.g} not found.")
			sys.exit(1)
	elif args.k:
		key_file = args.k.strip()
		if key_file.endswith(".key"):
			generate_otp(key_file)
		else:
			print("Error:  Please include *.key file")
			sys.exit(1)

		#load the key (open?)
		#generate OTP
	else:
		print("Error: use -g or -k flags")
		sys.exit(1)

		

if __name__=="__main__":
	main()