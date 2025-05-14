import os
import logging
import shutil
import zipfile
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import utils as asym_utils

# Logging configuration for both file and console output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

file_handler = logging.FileHandler('encryption_audit.log')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)

# Multi-factor authentication placeholder
def mfa_verification():
    logging.info("MFA verification required. Please complete MFA before proceeding...")
    # Simulating MFA success
    time.sleep(1)
    logging.info("MFA verification successful.")

# Function to pad data to be a multiple of 16 bytes (AES block size)
def pad_data(data):
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    return padder.update(data) + padder.finalize()

# Function to unpad decrypted data
def unpad_data(data):
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    return unpadder.update(data) + unpadder.finalize()

# Function to encrypt data using AES
def encrypt_data(data, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_data = pad_data(data)
    return encryptor.update(padded_data) + encryptor.finalize()

# Function to decrypt data using AES
def decrypt_data(ciphertext, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    return unpad_data(decrypted_padded_data)

# Function to generate HMAC for data integrity
def generate_hmac(key, data):
    h = HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    return h.finalize()

# Function to verify HMAC for data integrity
def verify_hmac(key, data, hmac_to_verify):
    h = HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    h.verify(hmac_to_verify)

# Function to calculate SHA-256 hash for file integrity check
def calculate_sha256(file_path):
    sha256_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256_hash.update(chunk)
    return sha256_hash.finalize()

# Function to compress files before encryption
def compress_file(input_file, output_file):
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(input_file)
    logging.info(f"Compressed {input_file} to {output_file}")

# Secure key derivation using PBKDF2 (Key Rotation Implementation)
def derive_new_key():
    password = b"strong_password"  # Key should be managed securely (e.g., via KMS)
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    return kdf.derive(password)

# Asymmetric key pair generation (RSA) for encrypting metadata
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
public_key = private_key.public_key()

# Serialize and save the private key for later decryption (in PEM format)
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PrivateFormat.PKCS8,
                                      encryption_algorithm=serialization.NoEncryption()))

# Digital signature function (RSA signing)
def sign_data(private_key, data):
    signature = private_key.sign(
        data,
        asym_padding.PSS(mgf=asym_padding.MGF1(hashes.SHA256()), salt_length=asym_padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return signature

# Path to the original SBOM file
original_file_path = "scan-result.json"
compressed_file_path = "compressed_sbom.zip"

# Compress the SBOM file before encryption
compress_file(original_file_path, compressed_file_path)

# Derive a new AES key (key rotation)
key = derive_new_key()

# Generate a random 16-byte initialization vector (IV)
iv = os.urandom(16)

# Read the compressed SBOM file
with open(compressed_file_path, "rb") as f:
    file_content = f.read()

# Encrypt the compressed SBOM file content
encrypted_data = encrypt_data(file_content, key, iv)

# Generate HMAC for the encrypted data
hmac_key = os.urandom(32)
hmac_value = generate_hmac(hmac_key, encrypted_data)

# Sign the encrypted data with the private key for authenticity
signature = sign_data(private_key, encrypted_data)

# Encrypt metadata (e.g., filename) using the public key
metadata = "compressed_sbom.zip"
encrypted_metadata = public_key.encrypt(
    metadata.encode(),
    asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
)

# Save the encrypted data, HMAC, signature, and encrypted metadata to files
encrypted_file_path = "encrypted_sbom.json"
hmac_file_path = "encrypted_sbom_hmac.json"
signature_path = "encrypted_sbom_signature.sig"
encrypted_metadata_path = "encrypted_metadata.json"

with open(encrypted_file_path, "wb") as f:
    f.write(encrypted_data)

with open(hmac_file_path, "wb") as f:
    f.write(hmac_value)

with open(signature_path, "wb") as f:
    f.write(signature)

with open(encrypted_metadata_path, "wb") as f:
    f.write(encrypted_metadata)

logging.info(f"Encrypted SBOM saved to {encrypted_file_path}")
logging.info(f"HMAC saved to {hmac_file_path}")
logging.info(f"Digital signature saved to {signature_path}")
logging.info(f"Encrypted metadata saved to {encrypted_metadata_path}")

# Define the backup directory and file path within the current working directory
backup_dir_primary = "backup_location_primary"
backup_dir_secondary = "backup_location_secondary"
backup_file = "encrypted_sbom.json"
backup_path_primary = os.path.join(backup_dir_primary, backup_file)
backup_path_secondary = os.path.join(backup_dir_secondary, backup_file)

# Ensure the backup directories exist
if not os.path.exists(backup_dir_primary):
    os.makedirs(backup_dir_primary)

if not os.path.exists(backup_dir_secondary):
    os.makedirs(backup_dir_secondary)

# Backup the encrypted file to two locations (redundant backup)
shutil.copy(encrypted_file_path, backup_path_primary)
shutil.copy(encrypted_file_path, backup_path_secondary)
logging.info(f"Backup of encrypted SBOM saved to {backup_path_primary} and {backup_path_secondary}")

# MFA verification before decryption
mfa_verification()

# Decrypt the encrypted data after verifying HMAC
with open(hmac_file_path, "rb") as f:
    saved_hmac_value = f.read()

with open(encrypted_file_path, "rb") as f:
    saved_encrypted_data = f.read()

# Verify the integrity of the encrypted data
try:
    verify_hmac(hmac_key, saved_encrypted_data, saved_hmac_value)
    logging.info("HMAC verification successful. The data is intact.")

    # Decrypt the data since the integrity check passed
    decrypted_data = decrypt_data(saved_encrypted_data, key, iv)

    # Save the decrypted content to a new file (decrypted_sbom.zip)
    decrypted_file_path = "decrypted_sbom.zip"
    with open(decrypted_file_path, "wb") as f:
        f.write(decrypted_data)

    logging.info(f"Decrypted SBOM saved to {decrypted_file_path}")

    # Verify that the decrypted data matches the original content
    if decrypted_data == file_content:
        logging.info("Success! The decrypted file matches the original SBOM.")
    else:
        logging.error("Error! The decrypted file does not match the original SBOM.")

except Exception as e:
    logging.error(f"Integrity check failed: {e}")

# File integrity check post-transfer
original_hash = calculate_sha256(encrypted_file_path)
transferred_hash_primary = calculate_sha256(backup_path_primary)
transferred_hash_secondary = calculate_sha256(backup_path_secondary)

if original_hash == transferred_hash_primary and original_hash == transferred_hash_secondary:
    logging.info("File integrity verified post-transfer at both locations.")
else:
    logging.error("Error! File integrity compromised during transfer.")
