import pandas as pd
import tkinter as tk
from tkinter import filedialog

class LinkedIn_Connections:
    def __init__(self, master):
        self.master = master
        self.master.title("File Selector")

        # Filename Display
        self.listbox = tk.Listbox(self.master, height=10, selectmode=tk.MULTIPLE)
        self.listbox.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Buttons
        tk.Button(self.master, text="Add File", command=self.add_file).pack(pady=5)
        tk.Button(self.master, text="Remove Selected", command=self.remove_selected).pack(pady=5)
        tk.Button(self.master, text="Generate DataFrame", command=self.generate_dataframe).pack(pady=10)

        self.file_paths = []

    # Add file to list
    def add_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if file_path:
            self.file_paths.append(file_path)
            self.update_listbox()

    # Remove file from list
    def remove_selected(self):
        selected_indices = self.listbox.curselection()
        for index in reversed(selected_indices):
            del self.file_paths[index]
        self.update_listbox()

    # Update the list of files
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for file_path in self.file_paths:
            self.listbox.insert(tk.END, file_path)

    def generate_dataframe(self):
        if self.file_paths:
            try:
                dfs = []
                for file_path in self.file_paths:
                    df = pd.read_csv(file_path)

                    df['SourceFile'] = file_path #indicates the source file, will need to be adjusted to show names later
                    dfs.append(df)

                combined_df = pd.concat(dfs, ignore_index=True)

                # TODO: where to work on generating the graphs
                print("Combined DataFrame:")
                print(combined_df)

            except Exception as e:
                print("Error opening the files with pandas:", e)

# Creating the main window and running it
root = tk.Tk()
root.geometry("400x300")
app = LinkedIn_Connections(root)

root.mainloop()