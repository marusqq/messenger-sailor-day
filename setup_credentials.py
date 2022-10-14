import os
import util

if __name__ == "__main__":

    print("setup_credentials.py will:\n"
          "1. Delete old credentials.json if it exists (so maybe make a backup?)\n"
          "2. Generate a new fernet_key\n"
          "3. Ask you for your fb login, password and 2FA base32 code for TOTP generation\n"
          "4. Encrypt them with fernet_key\n"
          "5. Set fernet_key as 'fernet_key' in your system variables\n"
          "6. Save your encrypted credentials in credentials.json\n")

    start = input('Enter y if you would like to continue:\n')
    if start.lower() != 'y':
        quit()
    credentials_file_name = 'credentials.json'

    print('-' * 50)
    print(f"Looking for old {credentials_file_name}....")
    # 1. if there is old credentials.json, delete it
    if os.path.exists(credentials_file_name):
        os.remove(credentials_file_name)
        print(f"Found, deleting!")
    else:
        print(f"Not found... Skipping delete")
    print('-' * 5)

    # 2. generate fernet_key
    print("Generating fernet_key...")
    fernet_key = util.generate_fernet_key()
    print("Generated!")
    print('-' * 5)

    # 3. get login, pass, totp
    print("Getting user credentials...")

    print("Enter login")
    login = util.get_user_credential("login", sensitive=False)

    print("Enter password")
    password = util.get_user_credential("password")

    print("Enter base32 code of 2FA")
    totp_code = util.get_user_credential("2FA base32 code", sensitive=False)
    print("Got user credentials!")

    print('-' * 5)

    # 4. encrypt them with fernet_key
    print("Encrypting credentials with fernet_key...")
    encrypted_login = util.fernet_encrypt(
        message_to_encrypt=login.encode(),
        key=fernet_key
    )
    encrypted_password = util.fernet_encrypt(
        message_to_encrypt=password.encode(),
        key=fernet_key
    )
    encrypted_totp_code = util.fernet_encrypt(
        message_to_encrypt=totp_code.encode(),
        key=fernet_key
    )
    print("Encrypted!")
    print('-' * 5)

    # 5. set fernet_key to env_variable
    print("Setting fernet_key environment value...")
    util.set_environment_value(
        env_path='fernet_key',
        env_value=fernet_key.decode()
    )

    print("Set!")
    print('-' * 5)

    # 6. save encrypted login, pass, totp to credentials.json
    print(f"Saving encrypted credentials to {credentials_file_name}...")
    credentials_dict = {
        "login": encrypted_login,
        "password": encrypted_password,
        "totp_code": encrypted_totp_code
    }

    util.write_credentials(credentials_dict)
    print('Saved!')
    print('-' * 5)

    print('Please reopen the terminal / source the venv again if you are using UNIX')
    print('-' * 50)
