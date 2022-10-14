def get_data_from_personal_data_file(path):
    with open(path) as f:
        base32_otp = f.readline()

    return base32_otp
