import shutil
import os
import sys
import pandas as pd
import argparse
import re

# --- Arguments and validation ---

parser = argparse.ArgumentParser(description="Organize photoshoot pictures based on a CSV file or a comma-separated list of image names.")
parser.add_argument("--output", default="export", help="Folder where to copy the selected images files.")
parser.add_argument("--input", default=".", help="Folder where the images files are located.")

group = parser.add_mutually_exclusive_group()
group.add_argument("--csv_file", help="Path to the CSV file. The third column should contain email addresses, and the fourth column should contain a comma-separated list of filenames (without extensions, e.g., 'IMG_0002'). All the referenced files must exist.")
group.add_argument("--list", help="Comma-separated list of image names (without extensions, e.g., 'IMG_0002'). All the referenced files must be in the same folder.")
args = parser.parse_args()

input_dir = args.input
output_dir = args.output
csv_file = args.csv_file
list_arg = args.list

# If neither --csv_file nor --list is specified, search for a CSV file in input_dir
if not csv_file and not list_arg:
    csv_candidates = [f for f in os.listdir(input_dir) if f.lower().endswith('.csv')]
    if len(csv_candidates) != 1:
        print(f"Error: Expected exactly one CSV file in the input folder, but found {len(csv_candidates)}. Please specify one with --csv_file.")
        sys.exit(1)
    csv_file = os.path.join(input_dir, csv_candidates[0])

# Validate CSV file if provided
if csv_file and (not os.path.isfile(csv_file) or not csv_file.endswith('.csv')):
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

# Parse files list
if csv_file:
    df = pd.read_csv(csv_file)
    df = df.iloc[:, [2, 3]]
    df.columns = ["email", "images"]
    images_list = set(img.strip().upper() + '.CR2' for item in df['images'] for img in item.split(','))
else:
    images_list = set(img.strip().upper() + '.CR2' for img in list_arg.split(','))

# Validate filenames and their existence
pattern = re.compile(r"^IMG_\d{4}\.CR2$")
for image in images_list:
    image_path = os.path.join(input_dir, image)
    if not pattern.match(image):
        print(f"Error: '{image}' has invalid file format. Expected format is 'IMG_0000.CR2'.")
        sys.exit(1)
    if not os.path.isfile(image_path):
        print(f"Error: '{image}' file does not exist in the input folder.")
        sys.exit(1)

# Copy files to the output directory
for image in images_list:
    image_path = os.path.join(input_dir, image)
    shutil.copy2(image_path, output_dir)

# Print the number of files copied and the output directory
print(f"Copied {len(images_list)} files to '{output_dir}'.")