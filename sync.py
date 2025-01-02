import os
import sys
import subprocess
from tkinter import Tk, filedialog, messagebox

def select_folder():
    """Prompt the user to select a folder if no folder path is provided."""
    root = Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder Containing Files to Sync")
    if not folder_path:
        messagebox.showwarning("No Folder Selected", "Please select a folder first.")
        return None
    return folder_path

def get_finder_tags(file_path):
    """Get Finder tags for a file using the tag command line tool."""
    tag_cmd = ["tag", "--list", file_path]
    result = subprocess.run(tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Failed to get tags for {file_path}: {result.stderr}")
        return []
    tags_str = result.stdout.strip()
    tags_lines = tags_str.split("\n")
    if len(tags_lines) > 1:
        tags = tags_lines[1].split(", ")
        return tags
    return []

def set_metadata_tags(file_path, tags):
    """Set metadata tags for a file using the tag command line tool."""
    tag_cmd = ["tag", "--set"] + tags + [file_path]
    result = subprocess.run(tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Failed to set tags for {file_path}: {result.stderr}")
    else:
        print(f"Set tags for {file_path}: {tags}")

def sync_tags(folder_path):
    """Recursively visit every file and sub-folder in the folder_path and sync Finder tags to metadata."""
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(("_tagged.pdf", "_tagged.txt", "_tagged.mp4", "_tagged.mkv", "_tagged.webm")):
                file_path = os.path.join(root, file_name)
                tags = get_finder_tags(file_path)
                if tags:
                    set_metadata_tags(file_path, tags)
                else:
                    print(f"No tags found for {file_name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        # Prompt the user to select a folder if no folder path is provided
        root = Tk()
        root.withdraw()  # Hide the root window
        folder_path = filedialog.askdirectory(title="Select Folder Containing Files to Tag")
        if not folder_path:
            print("No folder path provided.")
            sys.exit()

    if folder_path:
        print(f"Selected folder: {folder_path}")
        sync_tags(folder_path)
    else:
        print("No folder path provided.")