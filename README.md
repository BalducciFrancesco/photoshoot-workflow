# Photoshoot workflow helpers

Imagine you've just finished a busy weekend photoshoot, capturing hundreds of pictures for several participants. Then comes the hardest part: each participant would be best to receive their favorite shots, but first, you need to know which ones they want.

To accomplish this challenging task, you may send out a form (e.g. Google Forms) where each participant can select their preferred images by entering the filenames (like `IMG_0002`, `IMG_0045`, etc.). The form responses are collected in a CSV file, with each row containing the participant's email and their chosen images.

Once you've gathered everyone's selections, you need to develop the chosen images. This typically means opening the selected RAW files in Adobe Lightroom, performing edits and then exporting the final images as JPGs somewhere.

Instead of manually sorting, copying, editing, and emailing each set of images, this project provides helper scripts to automate the workflow:

1. **Organize**: Gather only the selected images into a dedicated folder.
2. **Develop**: Open the selected RAW files, perform your editing and retouching, and export the final images (as JPGs) to a separate folder.
3. **Send**: Automatically dispatch personalized emails to each participant, attaching only their chosen images.

## Workflow

### 1. Collecting Choices

- After the shoot, share a form with participants, asking them to select their favorite images by filename (e.g. `IMG_0002`).
- Export the form responses as a CSV file. The CSV should have:
  - The participant's email in the **third** column.
  - The selected image names (comma-separated, without extensions) in the **fourth** column.

### 2. Organizing Selected Images

Use `organize.py` to copy only the selected images into a new folder:

```sh
python organize.py --input path/to/all/images --csv_file path/to/responses.csv --output export
```

- This script reads the CSV, validates the filenames, and copies only the requested images (e.g. `IMG_0002.CR2`) into the `export` folder.
- You can also use a simple list of image names with `--list`.

### 3. Developing

- Open the images in the `export` folder (RAW files, e.g. `.CR2`) with your preferred photo editing software (such as Adobe Lightroom).
- Perform your edits, retouching, and adjustments as needed.
- Export the final images as `.JPG` files to a new folder (e.g. `export_jpg`).

### 4. Sending Images to Participants

After editing (and converting to JPG), use `send_email.py` to email each participant their images:

```sh
python send_email.py --input export --csv_file path/to/responses.csv --username your_gmail@gmail.com --send
```

- The script reads the CSV, matches each participant to their images, and sends personalized emails with the images attached.
- **Strongly suggested!** If you want to test without sending emails, omit `--send` and use `--output test_send` to save the emails as `.eml` files.

## Requirements

- Python 3
- `pandas` library

Install dependencies with:

```sh
pip install pandas
```

## Notes

- Filenames must follow the format `IMG_0000` (case-insensitive).
- The scripts expect RAW files (`.CR2`) for organizing and JPGs (`.JPG`) for sending.
- Always double-check the CSV columns and file existence before running the scripts.