'''
#!/usr/bin/python
'''
import sys
import argparse
import hmac
import string
import time
import math
from cryptography.fernet import Fernet

'''
checks if length is 64 (zero index) and if the string represents hexidecimal characters
'''
def	check_hex_character(key):
	if len(key) != 64:

#		print("./ft_otp: error: key must be 64 hexadecimal characters.")
		print(f"Error: Provided key has {len(key)} characters, but 64 are required.")
		sys.exit(1)
	if not all(c in string.hexdigits for c in key):
		print("./ft_otp: error: key must contain only hexadecimal characters.")
		sys.exit(1)


'''
function converts hex key to bytes and then saves it to ft_otp.key
Encryption produces binary data, which may not be printable or human-readable.

Writing this as a binary file ensures the information is without modifications or 
corruption caused by text encoding.
'''
def	make_encrypted_key(key):
	try:
		key_bytes = bytes.fromhex(key)
		#converts hex string to bytes
		encryption_key = Fernet.generate_key()
		#generate a Fernet encryption key
		cipher = Fernet(encryption_key)
		#create a Fernet object
		encrypted_key = cipher.encrypt(key_bytes)
		#encrypt the hexideximal key
		with open('ft_otp.key', 'wb') as f:
		#opens file in binary mode
			f.write(encryption_key + b'\n' + encrypted_key)
		#save the encryption key and encrypted data in the same file
		print("Key and encryption data were successfully stored in ft_otp.key")
	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)

def	decrypt_key(key_file):
	try:
		with open(key_file, "rb") as f:
			lines = f.readlines()
			encryption_key = lines[0].strip()
			#first line is the encryption key
			encrypted_key = lines[1].strip()
			#2nd line is the hex key we encrypted earlier
		cipher = Fernet(encryption_key)
		decrypted_key = cipher.decrypt(encrypted_key)
		#decypher the key
		otp = generate_totp(decrypted_key)
		print(f"your otp is: {otp}")
	except	Exception as e:
		print(f"Error: {e}")
		sys.exit(1)

'''
Generage an OTP using the HOTP algorithm (SHA1) and a time-based counter
pulled the information from RFC 4226

c is an 8-byte counter value, it increments after each OTP generation.
Therefore the counter must be sync'd with client and server
'''
def	generate_totp(secret):
		counter = math.floor(time.time() / 30).to_bytes(8, 'big')
		#8-byte big-endian counter
		hash_digest = hmac.digest(secret, counter, 'SHA1')
		#hmac.digest creates an hmac
		offset = hash_digest[-1] & 0xf
		#extract the 19th byte, mask to get the lower/last 4 bits
		#integer; the first byte is masked with a 0x7f.
		bin_code = ((hash_digest[offset] & 0x7f) << 24 |
			(hash_digest[offset + 1] & 0xff) << 16 |
			(hash_digest[offset + 2] & 0xff) << 8 |
			(hash_digest[offset + 3] & 0xff))
		# Only use the lower 31 bits of the result, this builds the 31-bit binary code
		#We treat the dynamic binary code as a 31-bit, unsigned, big-endian
		otp = bin_code % (10 ** 6)#or % 1,000,000
		padded_otp = str(otp).zfill(6)
		return padded_otp
		#generate the OTP (6 digits) and zero pad to ensure 6 digits

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
				check_hex_character(key)
				make_encrypted_key(key)
				print(f"For oathtool validation: oathtool --totp {key}")
		except FileNotFoundError:
			print(f"Error: File {args.g} not found.")
			sys.exit(1)
	elif args.k:
		key_file = args.k.strip()
		if key_file.endswith(".key"):
			decrypt_key(key_file)
		else:
			print("Error:  Please include *.key file")
			sys.exit(1)
	else:
		print("Error: use -g or -k flags")
		sys.exit(1)

if __name__=="__main__":
	main()
