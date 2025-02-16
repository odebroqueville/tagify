import os
import sys
import subprocess
from tkinter import Tk, filedialog, messagebox
import pymupdf
import json

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
    tags_str = result.stdout.replace(file_path,"").strip()
    # Split the tags_str based on the first occurrence of multiple spaces
    tags = [tag.strip() for tag in tags_str.split(",")] if tags_str else []
    if len(tags) > 0:
        print(f"Retrieved Finder tags for {file_path}: {', '.join(tags)}")
    else:
        print(f"No Finder tags found for {file_path}")
    return tags

def add_tags_to_pdf_metadata(pdf_path, tags):
    """Add generated tags to the metadata of the PDF."""
    doc = pymupdf.open(pdf_path)
    metadata = doc.metadata

    # Add or update the Keywords field with the generated tags
    metadata["keywords"] = ", ".join(tags)
    doc.set_metadata(metadata)

    # Save the updated PDF
    doc.save(pdf_path)
    doc.close()

def add_tags_to_video_metadata(video_path, tags):
    """Add generated tags to the metadata of the video."""
    tags_str = ", ".join(tags)
    ffmpeg_cmd = [
        "ffmpeg", "-loglevel", "quiet", "-y", "-i", video_path, "-metadata", f"comment={tags_str}", "-c", "copy", video_path
    ]
    subprocess.run(ffmpeg_cmd)

def add_tags_to_text_file(text_path, tags):
    """Add generated tags to the metadata of the text file."""
    metadata_path = text_path.replace(".txt", "_metadata.json")
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    metadata["tags"] = tags
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Updated metadata saved at: {metadata_path}")

def sync_tags(folder_path):
    """Recursively visit every file and sub-folder in the folder_path and sync Finder tags to metadata."""
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Check if it's actually a file
            if not os.path.isfile(file_path):
                continue
            
            # Skip hidden files and non-supported files
            if file_name.startswith("._") or not file_name.endswith((".pdf", ".txt", ".mp4", ".mkv", ".webm")):
                continue
            
            tags = get_finder_tags(file_path)
            if len(tags) > 0:
                if file_name.endswith(".pdf"):
                    add_tags_to_pdf_metadata(file_path, tags)
                elif file_name.endswith((".mp4", ".mkv", ".webm")):
                    add_tags_to_video_metadata(file_path, tags)
                elif file_name.endswith(".txt") and file_name.replace(".txt", "_metadata.json") in files:
                    add_tags_to_text_file(file_path, tags)

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
        sys.exit(0) # Exit with status code 0 indicating success
    else:
        print("No folder path provided.")
        sys.exit(1)  # Exit with status code 1 indicating an error