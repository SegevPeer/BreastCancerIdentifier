import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from keras.models import load_model
import numpy as np

# Load the saved model
model = load_model('my_model.keras')


def browse_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        # Load the image using PIL
        original_image = Image.open(file_path)

        # Convert the image to a PhotoImage object for displaying (enlarged version)
        enlarged_image = original_image.resize((200, 200))
        photo = ImageTk.PhotoImage(enlarged_image)

        # Display the enlarged image
        image_label.config(image=photo)
        image_label.photo = photo  # Keep a reference to prevent garbage collection

        # Set the file path label
        file_path_label.config(text="File Path: " + file_path)

        # Analyze the original image (without resizing) using the loaded model
        original_image = original_image.resize((48, 48))  # Resize for analysis
        img = np.array(original_image) / 255.0  # Normalize the image
        img = img.reshape((1, 48, 48, 3))  # Reshape for prediction

        # Classify the image using the loaded model
        result = model.predict(img)
        result_value = result[0][1]
        result_label.config(text=f"Result: {result_value:.2f} Malignant")

        # Adjust the label style based on the result
        if result_value > 0.8:
            result_label.config(fg="red", font=("Helvetica", 16, "bold"))
        else:
            result_label.config(fg="black", font=("Helvetica", 12))


def start_check():
    # Implement your image checking logic here
    pass


root = tk.Tk()
root.title("BCI")
# Maximize the window
root.state('zoomed')

title_label = tk.Label(root, text="BCI", font=("Helvetica", 24))
title_label.pack(pady=20)

image_label = tk.Label(root)
image_label.pack()

file_path_label = tk.Label(root, text="File Path: ")
file_path_label.pack()

browse_button = tk.Button(root, text="Browse", command=browse_image)
browse_button.pack()

result_label = tk.Label(root, text="Result: ")
result_label.pack()

quit_button = tk.Button(root, text="Quit", command=root.quit)
quit_button.pack(pady=20)

root.mainloop()
