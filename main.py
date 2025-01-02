import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
from PIL import Image, ImageDraw, ImageTk

# Global variable to store the path to the folder
folder_path = ""

def select_folder():
    global folder_path
    folder_path = filedialog.askdirectory(title="Select Folder Containing Files to Tag")
    if folder_path:
        messagebox.showinfo("Folder Selected", f"Selected folder: {folder_path}")
    return folder_path

def on_button_click(label, script):
    global folder_path
    if not folder_path:
        folder_path = select_folder()
    if folder_path:
        messagebox.showinfo("Button Clicked", f"You clicked the '{label}' button!")
        subprocess.run(["python", script, folder_path])
    else:
        messagebox.showwarning("No Folder Selected", "Please select a folder first.")

def create_rounded_button(canvas, text, command, y_position):
    width, height = 580, 100  # Adjust width to account for margins
    radius = 30

    # Create an image with rounded corners
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill="lightgrey", outline="darkgrey", width=2)

    # Convert the image to a PhotoImage
    photo_image = ImageTk.PhotoImage(image)

    # Create a label with the image
    button = tk.Label(canvas, image=photo_image, text=text, compound="center", font=("Helvetica", 24, "bold"), fg="darkgrey", bg="white")
    button.image = photo_image  # Keep a reference to avoid garbage collection
    button.place(x=10, y=y_position, width=580, height=100)  # Adjust x position to account for left margin
    button.bind("<Button-1>", lambda e: command())
    return button

def main():
    root = tk.Tk()
    root.title("Tag Manager")
    root.geometry("600x340")

    canvas = tk.Canvas(root, width=600, height=340, bg="white", highlightthickness=0)
    canvas.pack()

    # Create buttons
    button1 = create_rounded_button(canvas, "Select a folder to autotag", lambda: on_button_click("Select a folder to autotag", "tag.py"), 10)
    button2 = create_rounded_button(canvas, "Sync Finder tags to Metadata", lambda: on_button_click("Sync Finder tags to Metadata", "sync.py"), 120)
    button3 = create_rounded_button(canvas, "Open tags in a graph view", lambda: on_button_click("Open tags in a graph view", "graph.py"), 230)

    root.mainloop()

if __name__ == "__main__":
    main()