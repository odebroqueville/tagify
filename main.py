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
        subprocess.run(["python", script, folder_path])
    else:
        messagebox.showwarning("No Folder Selected", "Please select a folder first.")

def on_enter(event):
    event.widget.config(image=event.widget.hover_image, fg="lightgrey")

def on_leave(event):
    event.widget.config(image=event.widget.normal_image, fg="darkgrey")

# Event handlers
def on_click(event):
    button = event.widget
    # Unbind hover events
    button.unbind("<Enter>")
    button.unbind("<Leave>")
    
    # Update to clicked state
    button.config(image=button.clicked_image, fg="darkgrey")
    
    # Handle command/script
    if hasattr(button, 'command') and button.command:
        button.after(50, button.command)  # Delay command execution
    elif hasattr(button, 'script'):
        button.after(50, lambda: on_button_click(button.text, button.script, button))
    
    # Reset to normal state after delay
    button.after(100, lambda: [
        button.config(image=button.normal_image),
        button.bind("<Enter>", on_enter),
        button.bind("<Leave>", on_leave)
    ])

def create_rounded_button(canvas, text, script, y_position, command=None):
    width, height = 580, 100  # Adjust width to account for margins
    radius = 30

        # Create images with transparent background (RGBA)
    normal_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    hover_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    clicked_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Draw rounded rectangles for each state
    draw = ImageDraw.Draw(normal_image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill="lightgrey", outline=None)

    draw = ImageDraw.Draw(hover_image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill="darkgrey", outline=None)

    draw = ImageDraw.Draw(clicked_image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill="yellow", outline=None)

    # Convert to PhotoImage
    normal_photo_image = ImageTk.PhotoImage(normal_image)
    hover_photo_image = ImageTk.PhotoImage(hover_image)
    clicked_photo_image = ImageTk.PhotoImage(clicked_image)

    # Create button with transparent background
    button = tk.Label(
        canvas,
        image=normal_photo_image,
        text=text,
        compound="center",
        font=("Helvetica", 24, "bold"),
        fg="darkgrey",
        bg="white"
    )

    # Store references and attributes
    button.normal_image = normal_photo_image
    button.hover_image = hover_photo_image
    button.clicked_image = clicked_photo_image
    button.command = command
    button.text = text
    button.script = script

    # Bind the hover events
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

    # Bind the click event
    button.bind("<Button-1>", on_click)

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