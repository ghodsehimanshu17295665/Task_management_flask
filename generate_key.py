import secrets

secret_key = secrets.token_hex(32)
print("Generated SECRET_KEY:", secret_key)
