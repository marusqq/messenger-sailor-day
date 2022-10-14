import pyotp
from pathlib import Path
import util

data_file_path = Path("data.txt")
totp = pyotp.TOTP(util.get_data_from_personal_data_file(data_file_path))

