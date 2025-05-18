import smtplib
import os
import sys
import argparse
import getpass
from subprocess import call
from email.message import EmailMessage

# --- Arguments and validation ---

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Dispatch emails for edited pictures, as previously organized by `organize.py`.")
parser.add_argument("--csv_file", required=True, help="Path to the CSV file (check `organize.py` documentation for file schema).")
parser.add_argument("--input_folder", required=True, help="Path to the folder with the edited pictures.")
parser.add_argument("--username", required=True, help="Your Gmail address (sender).")
parser.add_argument("--send", default=False, help="Actually send the emails (default: dry run, do not send).")
args = parser.parse_args()

csv_file = args.csv_file
input_dir = args.input_folder
username = args.username
send_emails = bool(args.send)
password = getpass.getpass("Password for gmail account {}: ".format(args.username))

# Validate CSV file
if not os.path.isfile(csv_file) or not csv_file.endswith('.csv'):
    print(f"Error: {csv_file} is not a valid CSV file.")
    sys.exit(1)

# Validate or create output folder
if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
    print(f"Error: {input_dir} folder does not exist or is not a folder.")
    sys.exit(1)

# Validate that username is a gmail address
if not (isinstance(username, str) and username.lower().endswith('@gmail.com')):
    print(f"Error: {username} is not a valid Gmail address.")
    sys.exit(1)

# --- End arguments and validation ---

def send_email(filename, to):
    msg = EmailMessage()
    msg['Subject'] = 'Photoshoot takeout'
    msg['From'] = username
    msg['To'] = to
    msg.set_content('''
        Thanks again for participating! Attached to this e-mail you will find the pictures you have selected.\n
        Don't hesitate to contact me at [email] or [phone] if there's any issue or simply if you have some ideas for any future activity regarding photography :)
    ''')

    # Attach the image file
    with open(filename, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='image', subtype='jpeg', filename=filename)

    if(send_emails):
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
    else:
        with open('test_email.eml', 'wb') as eml_file:
            eml_file.write(msg.as_bytes())


call(["open", 'test_email.eml'])
