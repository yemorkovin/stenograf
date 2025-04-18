import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import lsb


class LSBSteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LSB Steganography")
        self.root.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Notebook для переключения между режимами
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка для скрытия сообщения
        self.hide_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.hide_tab, text="Hide Message")

        # Вкладка для извлечения сообщения
        self.extract_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.extract_tab, text="Extract Message")

        # Настройка вкладки Hide Message
        self.setup_hide_tab()

        # Настройка вкладки Extract Message
        self.setup_extract_tab()

    def setup_hide_tab(self):
        # Выбор исходного изображения
        tk.Label(self.hide_tab, text="Source Image:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.source_image_entry = tk.Entry(self.hide_tab, width=50)
        self.source_image_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.hide_tab, text="Browse", command=self.browse_source_image).grid(row=0, column=2, padx=5, pady=5)

        # Просмотр изображения
        self.image_label = tk.Label(self.hide_tab)
        self.image_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Ввод сообщения
        tk.Label(self.hide_tab, text="Message to hide:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.message_text = tk.Text(self.hide_tab, height=5, width=50)
        self.message_text.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        # Выбор выходного файла
        tk.Label(self.hide_tab, text="Output Image:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_image_entry = tk.Entry(self.hide_tab, width=50)
        self.output_image_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(self.hide_tab, text="Browse", command=self.browse_output_image).grid(row=3, column=2, padx=5, pady=5)

        # Кнопка скрытия сообщения
        tk.Button(self.hide_tab, text="Hide Message", command=self.hide_message).grid(row=4, column=1, pady=10)

    def setup_extract_tab(self):
        # Выбор изображения с сообщением
        tk.Label(self.extract_tab, text="Image with hidden message:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.hidden_image_entry = tk.Entry(self.extract_tab, width=50)
        self.hidden_image_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.extract_tab, text="Browse", command=self.browse_hidden_image).grid(row=0, column=2, padx=5,
                                                                                          pady=5)

        # Просмотр изображения
        self.hidden_image_label = tk.Label(self.extract_tab)
        self.hidden_image_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Вывод извлеченного сообщения
        tk.Label(self.extract_tab, text="Extracted message:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.extracted_message_text = tk.Text(self.extract_tab, height=5, width=50, state=tk.DISABLED)
        self.extracted_message_text.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        # Кнопка извлечения сообщения
        tk.Button(self.extract_tab, text="Extract Message", command=self.extract_message).grid(row=3, column=1, pady=10)

    def browse_source_image(self):
        filename = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")])
        if filename:
            self.source_image_entry.delete(0, tk.END)
            self.source_image_entry.insert(0, filename)
            self.display_image(filename, self.image_label)

    def browse_output_image(self):
        filename = filedialog.asksaveasfilename(defaultextension=".bmp", filetypes=[("BMP files", "*.bmp")])
        if filename:
            self.output_image_entry.delete(0, tk.END)
            self.output_image_entry.insert(0, filename)

    def browse_hidden_image(self):
        filename = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")])
        if filename:
            self.hidden_image_entry.delete(0, tk.END)
            self.hidden_image_entry.insert(0, filename)
            self.display_image(filename, self.hidden_image_label)

    def display_image(self, filename, label):
        try:
            img = Image.open(filename)
            img.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")

    def hide_message(self):
        source_image = self.source_image_entry.get()
        output_image = self.output_image_entry.get()
        message = self.message_text.get("1.0", tk.END).strip()

        if not source_image:
            messagebox.showerror("Error", "Please select source image")
            return
        if not output_image:
            messagebox.showerror("Error", "Please select output image")
            return
        if not message:
            messagebox.showerror("Error", "Please enter a message to hide")
            return

        try:
            lsb.hide_message(source_image, message, output_image)
            messagebox.showinfo("Success", "Message successfully hidden in the image")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to hide message: {str(e)}")

    def extract_message(self):
        hidden_image = self.hidden_image_entry.get()

        if not hidden_image:
            messagebox.showerror("Error", "Please select image with hidden message")
            return

        try:
            message = lsb.extract_message(hidden_image)
            self.extracted_message_text.config(state=tk.NORMAL)
            self.extracted_message_text.delete("1.0", tk.END)
            self.extracted_message_text.insert("1.0", message)
            self.extracted_message_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract message: {str(e)}")


def main():
    root = tk.Tk()
    app = LSBSteganographyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()