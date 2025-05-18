import shutil
import os
import sys
import pandas as pd
import argparse
import re
from subprocess import call

# --- Arguments and validation ---

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Organize photoshoot pictures based on a requested CSV file. The CSV file must have the third and fourth columns as follows: the third column should contain email addresses, and the fourth column should contain a comma-separated list of filenames (without extensions, e.g., 'IMG_0002'). All the referenced files must be in the same folder.")
parser.add_argument("--csv_file", required=True, help="Path to the CSV file (see documentation for file schema).")
parser.add_argument("--output_folder", required=True, help="Name of the output folder.")
args = parser.parse_args()

csv_file = args.csv_file
output_dir = args.output_folder

# Validate CSV file
if not os.path.isfile(csv_file) or not csv_file.endswith('.csv'):
    print(f"Error: {csv_file} is not a valid CSV file.")
    sys.exit(1)

# Validate or create output folder
if os.path.exists(output_dir):
    if not os.path.isdir(output_dir) or os.listdir(output_dir):
        print(f"Error: {output_dir} exists but is either not a folder or is not empty.")
        sys.exit(1)
else:
    os.makedirs(output_dir)

# --- End arguments and validation ---

df = pd.read_csv(csv_file)

df = df.iloc[:, [2, 3]]
df.columns = ["email", "images"]

images_list = set(img.strip().upper() + '.CR2' for item in df['images'] for img in item.split(','))

# Validate image filenames and existence
pattern = re.compile(r"^IMG_\d{4}\.CR2$")
for image in images_list:
    if not pattern.match(image):
        print(f"Error: '{image}' has invalid file format. Expected format is 'IMG_0000.CR2'.")
        sys.exit(1)
    if not os.path.isfile(image):
        print(f"Error: '{image}' file does not exist in this folder.")
        sys.exit(1)

for f in images_list:
    shutil.copy2(f, output_dir)

call(["open", output_dir])