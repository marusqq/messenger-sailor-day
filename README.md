# messenger-sailor-day
Sends an image corresponding the needed day of the Crabs meme to my messenger groups

For setup:
- First setup 2fa on facebook and save that 16 letter 32base code (also save it to your favourite authenticator so you can actually use your account)
- Create venv from requirements.txt
- Run **setup_credentials.py** to setup credentials.json. 
  - Your credentials will be encoded and saved into credentials.json, the fernet_key (used in encoding) will be saved in your environment variables. Tested only on Linux though but should work for Windows as well
  - After setup_credential, reopen terminal so Linux catches the new env variable
- After set up, change group_ids for groups/people you want to send the vids to
- Setup video_group_url (url for where last 7 messages are sent vids so forwarding the videos would be possible)

