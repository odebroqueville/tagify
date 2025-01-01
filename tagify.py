import os
import sys
import pymupdf
from keybert import KeyBERT
import logging
import subprocess
import whisper
import json
import inflect

# Set the environment variable to disable parallelism for tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize KeyBERT
kw_model = KeyBERT()

# Initialize the inflect engine
p = inflect.engine()

def get_filename_without_extension(video_path):
    """Extract the filename without extension from a video path."""
    filename_with_extension = os.path.basename(video_path)  # Get the filename with extension
    filename_without_extension = os.path.splitext(filename_with_extension)[0]  # Remove the extension
    return filename_without_extension

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_audio_with_original_format(video_path, output_dir):
    """Extract audio from a video file, preserving the original format."""
    # Get the audio codec using ffprobe
    ffprobe_cmd = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name", "-of",
        "default=noprint_wrappers=1:nokey=1", video_path
    ]
    result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    audio_codec = result.stdout.strip()
    
    # Map codec to file extension
    codec_to_extension = {
        "aac": "aac",
        "mp3": "mp3",
        "vorbis": "ogg",
        "opus": "opus",
        "flac": "flac",
        "pcm_s16le": "wav",
    }
    file_extension = codec_to_extension.get(audio_codec, "m4a")  # Default to m4a if unknown
    
    # Create the output directory if it doesn't exist
    video_name_without_extension = get_filename_without_extension(video_path)
    output_dir = os.path.join(output_dir, video_name_without_extension)
    os.makedirs(output_dir, exist_ok=True)
    
    audio_output_path = os.path.join(output_dir, f"{video_name_without_extension}.{file_extension}")

    # Check if the audio file already exists
    if os.path.exists(audio_output_path):
        print(f"Audio already extracted: {audio_output_path}")
        return audio_output_path

    # Extract audio if it doesn't already exist
    ffmpeg_cmd = [
        "ffmpeg", "-i", video_path, "-vn", "-acodec", "copy", "-f", file_extension, audio_output_path
    ]
    subprocess.run(ffmpeg_cmd)
    return audio_output_path
    
def transcribe_audio_with_language_detection(audio_path):
    """Transcribe audio with language detection and save as JSON."""
    # Extract the file extension from audio_path
    output_dir = os.path.dirname(audio_path)
    output_json_path = os.path.join(output_dir, f"{get_filename_without_extension(audio_path)}_transcription.json")

    
    # Check if the transcription file already exists
    if os.path.exists(output_json_path):
        print(f"Transcription already exists: {output_json_path}")
        return output_json_path
    
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    detected_language = result.get("language", "unknown")
    transcript = result["text"]
    
    # Create the JSON structure
    transcription_data = {
        "language": detected_language,
        "transcript": transcript
    }

    # Save the transcription data to a JSON file
    with open(output_json_path, 'w') as json_file:
        json.dump(transcription_data, json_file, ensure_ascii=False, indent=4)

    print(f"Transcription saved to {output_json_path}")
    return output_json_path

def generate_tags(text, model, top_n=5):
    """Generate tags using KeyBERT."""
    keywords = model.extract_keywords(text, top_n=top_n)
    return [kw[0] for kw in keywords]

def filter_singular_tags(tags):
    """Filter out tags that are in plural form."""
    return [tag for tag in tags if not p.singular_noun(tag)]

def add_tags_to_pdf_metadata(pdf_path, tags):
    """Add generated tags to the metadata of the PDF."""
    tags = filter_singular_tags(tags)
    doc = pymupdf.open(pdf_path)
    metadata = doc.metadata

    # Add or update the Keywords field with the generated tags
    metadata["keywords"] = ", ".join(tags)
    doc.set_metadata(metadata)

    # Save the updated PDF
    output_path = pdf_path.replace(".pdf", "_tagged.pdf")
    doc.save(output_path)
    doc.close()
    return output_path

def add_tags_to_video_metadata(video_path, tags):
    """Add generated tags to the metadata of the video."""
    tags = filter_singular_tags(tags)
    output_path = video_path.replace(".mp4", "_tagged.mp4").replace(".mkv", "_tagged.mkv").replace(".webm", "_tagged.webm")
    
    # Check if the tagged file already exists
    if os.path.exists(output_path):
        overwrite = input(f"File '{output_path}' already exists. Overwrite? [y/N] ").strip().lower()
        if overwrite != 'y':
            print("Not overwriting - skipping")
            return None

    tags_str = ", ".join(tags)
    ffmpeg_cmd = [
        "ffmpeg", "-i", video_path, "-metadata", f"comment={tags_str}", "-c", "copy", output_path
    ]
    subprocess.run(ffmpeg_cmd)
    print(f"Tagged video saved at: {output_path}")
    return output_path

def get_finder_tags(file_path):
    """Get Finder tags using the tag command line tool."""
    tag_cmd = ["tag", "--list", file_path]
    result = subprocess.run(tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Failed to get Finder tags for {file_path}: {result.stderr}")
        return []
    tags_str = result.stdout.strip()
    # Split the output by newlines and take the second line as the tags
    tags_lines = tags_str.split("\n")
    if len(tags_lines) > 1:
        tags = tags_lines[1].split(", ")
        tags = filter_singular_tags(tags)
        print(f"Retrieved Finder tags for {file_path}: {', '.join(tags)}")
    else:
        tags = []
        print(f"No Finder tags found for {file_path}")
    print("----------------")
    return tags

def set_finder_tags(file_path, tags):
    """Set Finder tags using the tag command line tool."""
    tags = filter_singular_tags(tags)
    tags_str = ",".join(tags)
    tag_cmd = ["tag", "--set", tags_str, file_path]
    result = subprocess.run(tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Failed to set Finder tags for {file_path}: {result.stderr}")
    else:
        print(f"Set Finder tags for {file_path}: {tags_str}")

def process_folder(folder_path):
    """Process all PDFs and videos in a folder and its sub-folders to generate tags and update metadata."""
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # Initialize the tagged flag
            tagged = False
            
            # If the file is already tagged, then set the flag tagged to True
            if file_name.endswith("_tagged.pdf") or file_name.endswith("_tagged.mp4") or file_name.endswith("_tagged.mkv") or file_name.endswith("_tagged.webm"):
                tagged = True
            
            # Skip hidden files and non-supported files
            if file_name.startswith("._") or not file_name.endswith((".pdf", ".txt", ".mp4", ".mkv", ".webm")):
                continue

            file_path = os.path.join(root, file_name)
            
            # Check if it's actually a file
            if not os.path.isfile(file_path):
                continue
            
            try:
                tags = []
                if file_name.endswith(".pdf"):
                    if not tagged:
                        # Extract text from the PDF
                        text = extract_text_from_pdf(file_path)

                        # Generate tags
                        tags = generate_tags(text, kw_model)
                        print(f"Tags for {file_name}: {tags}")

                        # Add tags to the PDF metadata
                        updated_pdf_path = add_tags_to_pdf_metadata(file_path, tags)
                        print(f"Tagged PDF saved at: {updated_pdf_path}")
                    else:
                        updated_pdf_path = file_path
                        # Read tags from the PDF metadata
                        doc = pymupdf.open(file_path)
                        metadata = doc.metadata
                        tags_str = metadata.get("keywords", "")
                        tags = tags_str.split(", ") if tags_str else []
                        doc.close()
                    
                    # Check if Finder tags are already set
                    finder_tags = get_finder_tags(updated_pdf_path)
                    if not finder_tags:
                        # Set Finder tags
                        set_finder_tags(updated_pdf_path, tags)

                elif file_name.endswith(".txt"):
                    if not tagged:
                        # Extract text from the text file
                        with open(file_path, 'r') as file:
                            text = file.read()

                        # Generate tags
                        tags = generate_tags(text, kw_model)
                        print(f"Tags for {file_name}: {tags}")

                        # Save tags in a separate metadata file
                        metadata_path = file_path.replace(".txt", "_metadata.json")
                        with open(metadata_path, 'w') as metadata_file:
                            json.dump({"tags": tags}, metadata_file)
                        print(f"Metadata saved at: {metadata_path}")
                    else:
                        # Read tags from the metadata file
                        metadata_path = file_path.replace(".txt", "_metadata.json")
                        with open(metadata_path, 'r') as metadata_file:
                            metadata = json.load(metadata_file)
                            tags = metadata.get("tags", [])
                    
                    # Check if Finder tags are already set
                    finder_tags = get_finder_tags(file_path)
                    if not finder_tags:
                        # Set Finder tags
                        set_finder_tags(file_path, tags)

                elif file_name.endswith((".mp4", ".mkv", ".webm")):
                    if not tagged:
                        # Extract audio
                        audio_path = extract_audio_with_original_format(file_path, root)
                        print(f"Audio extracted from {file_name} to {audio_path}")

                        # Transcribe audio
                        output_json_path = transcribe_audio_with_language_detection(audio_path)
                        # Load the JSON file to get the language and transcript
                        with open(output_json_path, 'r') as json_file:
                            transcription_data = json.load(json_file)
                            language = transcription_data["language"]
                            transcript = transcription_data["transcript"]
                        print(f"Transcription ({language}): {transcript}")

                        # Generate tags
                        tags = generate_tags(transcript, kw_model)
                        print(f"Tags for {file_name}: {tags}")

                        # Add tags to the video metadata
                        updated_video_path = add_tags_to_video_metadata(file_path, tags)
                        if updated_video_path is None:
                            continue  # Skip setting Finder tags if not overwriting
                        print(f"Tagged video saved at: {updated_video_path}")
                    else:
                        updated_video_path = file_path
                        # Read tags from the video metadata
                        tags_str = subprocess.run(
                            ["ffprobe", "-v", "error", "-show_entries", "format=tags:stream=tags", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
                            stdout=subprocess.PIPE, text=True
                        ).stdout.strip()
                        tags = tags_str.split(", ") if tags_str else []
                    
                    # Check if Finder tags are already set
                    finder_tags = get_finder_tags(updated_video_path)
                    if not finder_tags:
                        # Set Finder tags
                        set_finder_tags(updated_video_path, tags)

            except pymupdf.FileDataError as e:
                print(f"Error processing PDF {file_name}: {str(e)}")
            except Exception as e:
                print(f"Unexpected error processing {file_name}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        process_folder(folder_path)
    else:
        print("No folder path provided.")