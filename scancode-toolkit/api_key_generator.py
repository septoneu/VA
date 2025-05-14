import secrets

def generate_api_key():
    return secrets.token_hex(16)  # Generates a 32-character hexadecimal string

# Generate and print the API key
api_key = generate_api_key()
print(f"Generated API Key: {api_key}")
