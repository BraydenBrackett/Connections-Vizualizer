import pandas as pd
import tkinter as tk
from tkinter import filedialog
from pyvis import network as net
import networkx as nx
import webbrowser
import janitor
import sys
import matplotlib as mlt
import matplotlib.pyplot as plt
import os

def generate_graph(file_names, threshold):
  
  colors = ["#0046FF", "#FF0000", "#F0FF00", "#49FF00"]

  repeated_color_code = "#898989"
  data_company = [[]] * len(file_names)
  data_positions = [[]] * len(file_names)
  companies_by_person = [[]] * len(file_names)
  data_df = [[]] * len(file_names)

  combined_dfs = []

  for index in range(len(file_names)):
    df = pd.read_csv(file_names[index], skiprows=2)

    df = (
      df
      .clean_names() # remove spacing and capitalization
      .drop(columns=['first_name', 'last_name', 'email_address']) # drop for privacy
      .dropna(subset=['company', 'position']) # drop missing values in company and position
      .to_datetime('connected_on', format='%d %b %Y')
    )

    """## Simple EDA"""

    df['company'].value_counts().head(10).plot(kind="barh").invert_yaxis()

    df['position'].value_counts().head(10).plot(kind="barh").invert_yaxis()

    df['connected_on'].hist(xrot=35, bins=15)

    """### Remove freelance and self-employed titles"""

    pattern = "freelance|self-employed"
    df = df[~df['company'].str.contains(pattern, case=False)]

    df['user_id'] = index

    combined_dfs.append(df)


  for file_idx in range(len(file_names)):
    df_ori = pd.read_csv(file_names[file_idx], skiprows=2)

    df = (
      df_ori
      .clean_names() # remove spacing and capitalization
      .drop(columns=['first_name', 'last_name', 'email_address']) # drop for privacy
      .dropna(subset=['company', 'position']) # drop missing values in company and position
      .to_datetime('connected_on', format='%d %b %Y')
    )

    """## Simple EDA"""

    df['company'].value_counts().head(10).plot(kind="barh").invert_yaxis()

    df['position'].value_counts().head(10).plot(kind="barh").invert_yaxis()

    df['connected_on'].hist(xrot=35, bins=15)


    """### Remove freelance and self-employed titles"""

    pattern = "freelance|self-employed"
    df = df[~df['company'].str.contains(pattern, case=False)]

    """## Aggregate sum of connections for companies"""

    companies_by_person[file_idx] = list(df['company'].unique())

    df_company = df['company'].value_counts().reset_index()
    df_company.columns = ['company', 'count']
    df_company = df_company.sort_values(by="count", ascending=False)

    """## Aggregate sum of connections for positions"""

    df_position = df['position'].value_counts().reset_index()
    df_position.columns = ['position', 'count']
    df_position['company'] = df['company']
    df_position = df_position.sort_values(by="count", ascending=False)

    ## Creating the network
    df_company_reduced = df_company.loc[df_company['count']>=3]

    df_position_reduced = df_position.loc[df_position['count']>=2]

    
    data_df[file_idx] = df
    data_company[file_idx] = df_company_reduced
    data_positions[file_idx] = df_position_reduced

  combined_dfs = pd.concat(combined_dfs, ignore_index=True)

  seen = set()
  repeated_company = set()
  for l in data_company:
    for i in set(l['company']):
      if i in seen:
        repeated_company.add(i)
      else:
        seen.add(i)

  seen = set()
  repeated_positions = set()
  for l in data_positions:
    for i in set(l['position']):
      if i in seen:
        repeated_positions.add(i)
      else:
        seen.add(i)


  # initialize graph
  g = nx.Graph()
  g.add_node('You') # intialize yourself as central

  # use iterrows tp iterate through the data frame
  for idx in range(len(file_names)):
    df_company_reduced = data_company[idx]
    df_position_reduced = data_positions[idx]
    df = data_df[idx]

    for _, row in df_company_reduced.iterrows():

      # store company name and count
      company = row['company']
      count = row['count']

      title = f"<b>{company}</b> – {count}"
      positions = set([x for x in df[company == df['company']]['position']])
      positions_li = positions
      positions = ''.join('<li>{}</li>'.format(x) for x in positions)

      position_list = f"<ul>{positions}</ul>"
      hover_info = title + position_list

      for position in positions_li:

        size_df = len(df[(df['position'] == position) & (df['company'] == company)])
        
        if size_df >= 2:
          comb_name = str(position) + " - " + str(company)
          
          matches = []
          match_id = 0
          for person in range(len(file_names)):

            cnt = len(combined_dfs[(combined_dfs['position'] == position) & (combined_dfs['company'] == company) & (combined_dfs['user_id'] == person)])

            if cnt > 0:

              match_id = person
              matches.append(person)
            
          if len(matches) >= 2:
            g.add_node(comb_name, size= size_df, title=hover_info, color=repeated_color_code, label = position)
          else:
            g.add_node(comb_name, size= size_df, title=hover_info, color=colors[match_id], label = position) 
          

          g.add_edge(company, comb_name, color='grey')

      if company in repeated_company:
        g.add_node(company, size=count*2, title=hover_info, color=repeated_color_code)
      else:
        g.add_node(company, size=count*2, title=hover_info, color= colors[idx])
      g.add_edge('You', company, color='grey')

  names = [os.path.splitext(os.path.basename(x))[0] for x in file_names]
  mlt.rcParams['toolbar'] = 'None'
  plt.close('all')
  fig, ax = plt.subplots(figsize=(2.5, 2))
  legend_handles = [plt.Line2D([0], [0], marker='o', color='w', label=label, markerfacecolor=color, markersize=10) for label, color in zip(names, colors)]
  ax.legend(handles=legend_handles, loc='upper right')
  ax.set_xticks([])
  ax.set_yticks([])
  ax.set_xticklabels([])
  ax.set_yticklabels([])

  # generate the graph
  nt = net.Network(height='850px', width='1800px', bgcolor="white", font_color='black')
  nt.from_nx(g)
  nt.hrepulsion(160, 0, 300, 0.01, 0.09)
  nt.write_html('company_graph.html')
  webbrowser.open('company_graph.html', new=1)
  plt.show()


class LinkedIn_Connections:
    def __init__(self, master):
        self.master = master
        self.master.title("File Selector")
        self.file_paths = []

        # Filename Display
        self.listbox = tk.Listbox(self.master, height=10, selectmode=tk.MULTIPLE)
        self.listbox.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Buttons
        tk.Button(self.master, text="Add File", command=self.add_file).pack(pady=5)
        tk.Button(self.master, text="Remove Selected", command=self.remove_selected).pack(pady=5)

        # Slider
        self.threshold = 0

        def on_change(value):
          self.threshold = value
        label = tk.Label(root, text="Node Threshold:")
        label.pack(pady=2)

        slider = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, command=on_change)
        slider.pack(pady=0)

        # Generator
        tk.Button(self.master, text="Generate DataFrame", command=self.generate_dataframe).pack(pady=10)

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

    # Create GUI 
    def generate_dataframe(self):
        if self.file_paths:
            dfs = []
            for file_path in self.file_paths:
                dfs.append(file_path)
            generate_graph(dfs, self.threshold)

def on_closing():
    root.destroy()
    sys.exit(0)

# Creating the main window and running it
root = tk.Tk()
root.geometry("800x600")
app = LinkedIn_Connections(root)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
