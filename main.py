import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
from PIL import Image, ImageDraw, ImageTk

# Global variable to store the path to the folder
folder_path = ""

def select_folder():
    global folder_path
    folder_path = filedialog.askdirectory(title="Select Folder Containing Files to Tag")
    return folder_path

def on_button_click(label, script, button):
    global folder_path
    if not folder_path:
        folder_path = select_folder()
    if folder_path:
        # Temporarily change the border thickness to 0
        button.config(image=button.clicked_image)
        subprocess.run(["python", script, folder_path])
        # Revert the border thickness after the command is executed
        button.config(image=button.normal_image)
    else:
        messagebox.showwarning("No Folder Selected", "Please select a folder first.")

def on_enter(event):
    event.widget.config(image=event.widget.hover_image, fg="lightgrey")

def on_leave(event):
    event.widget.config(image=event.widget.normal_image, fg="darkgrey")

def create_rounded_button(canvas, text, script, y_position, command=None):
    width, height = 580, 100  # Adjust width to account for margins
    radius = 30

    # Create an image with rounded corners for normal state
    normal_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(normal_image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill="lightgrey", outline="darkgrey", width=2)

    # Create an image with rounded corners for hover state
    hover_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(hover_image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill="darkgrey", outline="darkgrey", width=2)

    # Create an image with rounded corners for clicked state (border thickness 0)
    clicked_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(clicked_image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill="lightgrey", outline="darkgrey", width=0)

    # Convert the images to PhotoImage
    normal_photo_image = ImageTk.PhotoImage(normal_image)
    hover_photo_image = ImageTk.PhotoImage(hover_image)
    clicked_photo_image = ImageTk.PhotoImage(clicked_image)

    # Create a label with the normal image
    button = tk.Label(canvas, image=normal_photo_image, text=text, compound="center", font=("Helvetica", 24, "bold"), fg="darkgrey", bg="white")
    button.normal_image = normal_photo_image  # Keep a reference to avoid garbage collection
    button.hover_image = hover_photo_image  # Keep a reference to avoid garbage collection
    button.clicked_image = clicked_photo_image  # Keep a reference to avoid garbage collection

    # Bind the hover events
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

    # Bind the click event
    if command:
        button.bind("<Button-1>", lambda event: command())
    else:
        button.bind("<Button-1>", lambda event: on_button_click(text, script, button))

    # Place the button on the canvas
    button.place(x=10, y=y_position, width=580, height=100)  # Adjust x position to account for left margin
    return button

def main():
    root = tk.Tk()
    root.title("Tag Manager")
    root.geometry("600x450")  # Adjusted height to fit the new button

    canvas = tk.Canvas(root, width=600, height=450, bg="white", highlightthickness=0)
    canvas.pack()

    # Create buttons
    button1 = create_rounded_button(canvas, "Select a folder to autotag", "tag.py", 10)
    button2 = create_rounded_button(canvas, "Sync Finder tags to Metadata", "sync.py", 120)
    button3 = create_rounded_button(canvas, "Open tags in a graph view", "graph.py", 230)
    button4 = create_rounded_button(canvas, "Close and Quit", None, 340, command=root.quit)

    root.mainloop()

if __name__ == "__main__":
    main()