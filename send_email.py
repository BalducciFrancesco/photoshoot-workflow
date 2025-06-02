import smtplib
import os
import sys
import argparse
import getpass
import pandas as pd
import re
from email.message import EmailMessage

# --- Arguments and validation ---

parser = argparse.ArgumentParser(description="Dispatch emails for edited pictures, as previously organized by `organize.py`.")
parser.add_argument("--input", default=".", help="Folder where the images files are located.")
parser.add_argument("--csv_file", help="Path to the CSV file. The third column should contain email addresses, and the fourth column should contain a comma-separated list of filenames (without extensions, e.g., 'IMG_0002'). All the referenced files must exist.")
parser.add_argument("--username", required=True, help="Your Gmail address (sender).")
parser.add_argument("--send", action="store_true", help="Actually send the emails (default: dry run, do not send).")
parser.add_argument("--output", default="test_send", help="Folder where to store the .eml files if not sending emails (default: ./test_send).")
args = parser.parse_args()

input_dir = args.input
csv_file = args.csv_file
username = args.username
send_emails = args.send
output_dir = args.output

password = getpass.getpass("Password for gmail account {}: ".format(args.username))

# If --csv_file is not specified, search for exactly one CSV in input_dir
if not csv_file:
    csv_candidates = [f for f in os.listdir(input_dir) if f.lower().endswith('.csv')]
    if len(csv_candidates) != 1:
        print(f"Error: Expected exactly one CSV file in the input folder, but found {len(csv_candidates)}. Please specify one with --csv_file.")
        sys.exit(1)
    csv_file = os.path.join(input_dir, csv_candidates[0])

# Validate CSV file
if not os.path.isfile(csv_file) or not csv_file.endswith('.csv'):
    print(f"Error: {csv_file} is not a valid CSV file.")
    sys.exit(1)

# Validate that username is a gmail address
if not (isinstance(username, str) and username.lower().endswith('@gmail.com')):
    print(f"Error: {username} is not a valid Gmail address.")
    sys.exit(1)

# If not sending emails, --output must be specified and valid
if not send_emails:
    if not output_dir:
        print("Error: --output is required when not sending emails (--send not specified).")
        sys.exit(1)
    if os.path.exists(output_dir):
        if not os.path.isdir(output_dir) or os.listdir(output_dir):
            print(f"Error: {output_dir} exists but is either not a folder or is not empty.")
            sys.exit(1)
    else:
        os.makedirs(output_dir)

# --- End arguments and validation ---

# Read CSV and prepare emails
df = pd.read_csv(csv_file)
df = df.iloc[:, [2, 3]]
df.columns = ["email", "images"]

recipients = [] # List to hold recipient information (email and filepaths)
pattern = re.compile(r"^IMG_\d{4}\.JPG$", re.IGNORECASE)
all_files_in_folder = set(f for f in os.listdir(input_dir) if pattern.match(f))
all_files_to_send = set()

# For each receipient, check and prepare the files to send  
for idx, row in df.iterrows(): 
    req_addr = row['email']
    req_images = [img.strip().upper() + '.JPG' for img in row['images'].split(',')]
    filepaths = []
    for req_image in req_images:
        if not pattern.match(req_image):
            print(f"Error: '{req_image}' has invalid file format. Expected format is 'IMG_0000.JPG'.")
            sys.exit(1)
        image_path = os.path.join(input_dir, req_image)
        if not os.path.isfile(image_path):
            print(f"Error: '{req_image}' file does not exist in the input folder.")
            sys.exit(1)
        filepaths.append(image_path)
        all_files_to_send.add(req_image)
    if not filepaths:
        print(f"Error: Recipient '{req_addr}' does not have any files to send.")
        sys.exit(1)
    recipients.append({
        "email": req_addr,
        "filepaths": filepaths,
        "images": req_images
    })

# Recap before sending
print(f"\nAbout to send {len(recipients)} emails, with {sum(len(r['filepaths']) for r in recipients)} files in total.")

# Check for unused files in the input folder
unused_files = all_files_in_folder - all_files_to_send
if unused_files:
    print(f"WARNING: There are {len(unused_files)} extra image(s) files present in the input folder that will not be sent:")
    for fname in sorted(unused_files):
        print(f"  - {fname}")
    print("Did you use `organize.py` to prepare the files?\n")

input("Press Enter to continue and send emails (or Ctrl+C to abort)..")

def send_email(to, filepaths):
    msg = EmailMessage()
    msg['Subject'] = 'Photoshoot takeout'
    msg['From'] = username
    msg['To'] = to
    msg.set_content('''
        Hi,
                    
        Thanks again for participating! Attached to this e-mail you will find the pictures you have selected.

        Don't hesitate to contact me if there's any issue or simply if you have some ideas for any future activity regarding photography :)
                    
        Best regards,
        Your photographer

                    
        (This is an automated message. Check out my script on GitHub if you wish to contribute: https://github.com/BalducciFrancesco/photoshoot-workflow)
    ''')

    for filepath in filepaths:
        with open(filepath, 'rb') as f:
            file_data = f.read()
            attach_name = os.path.basename(filepath)
            msg.add_attachment(file_data, maintype='image', subtype='jpeg', filename=attach_name)

    print(f"Sending email to {to} with files: {','.join(os.path.splitext(os.path.basename(fp))[0] for fp in filepaths)}")
    if send_emails:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
    else:
        eml_name = to.replace("@", "_at_") + '.eml'
        eml_path = os.path.join(output_dir, eml_name)
        with open(eml_path, 'wb') as eml_file:
            eml_file.write(msg.as_bytes())

for recipient in recipients:
    send_email(recipient["email"], recipient["filepaths"])