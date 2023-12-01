import pandas as pd
import tkinter as tk
from tkinter import filedialog
import recordlinkage
import os

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


    #function for simplifing down companies
    def simplify_companies(self, df):
        # Create an indexer and compare the company names using string similarity
        indexer = recordlinkage.Index()
        indexer.full()
        candidates = indexer.index(df)

        compare_cl = recordlinkage.Compare()

        # String similarity comparison
        compare_cl.string('Company', 'Company', method='jarowinkler', threshold=0.8)

        # Compute the similarity scores
        features = compare_cl.compute(candidates, df)

        # Define a threshold for considering matches
        threshold = 0.8

        # Get pairs of similar records based on the threshold
        matches = features[features.sum(axis=1) > threshold]

        # Create a dictionary to map original company names to simplified names
        company_mapping = {}

        # Update the mapping with the pairs of similar records
        for idx1, idx2 in matches.index:
            name1 = df.loc[idx1, 'Company']
            name2 = df.loc[idx2, 'Company']
            
            if name1 not in company_mapping:
                company_mapping[name1] = name1
            
            if name2 not in company_mapping:
                company_mapping[name2] = name1

        # Apply the mapping to create a new 'Simplified Company' column
        df['Simplified Company'] = df['Company'].map(company_mapping)

        # Display the cleaned DataFrame
        print(df[['Company', 'Simplified Company']])


    def generate_dataframe(self):
        if self.file_paths:
            try:
                dfs = []
                for file_path in self.file_paths:
                    #print(os.path.splitext(os.path.basename(file_path)))
                    df = pd.read_csv(file_path, skiprows=3)

                    df['SourceFile'] = file_path #name of linkedin data is currently derrived from the existing files name (hence name files as people)
                    dfs.append(df)

                combined_df = pd.concat(dfs, ignore_index=True)
                #self.simplify_companies(combined_df) - JUST ignore this for the timing being

            except Exception as e:
                print("Error opening the files with pandas:", e)

    #def create_graph(self):
        #TODO: generate graphs here

# Creating the main window and running it
root = tk.Tk()
root.geometry("800x600")
app = LinkedIn_Connections(root)

root.mainloop()