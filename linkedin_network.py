
#!pip install pyjanitor pyvis --quiet
#!pip install --upgrade ipykernel

import pandas as pd
import janitor
#import datetime

from IPython.core.display import display, HTML
from pyvis import network as net
import networkx as nx


file_names = ["Connections.csv", "Connections_2.csv"]
colors = ["#0046FF", "#FF0000", "#F0FF00", "#49FF00"]
repeated_color_code = "#898989"
data_company = [[]] * len(file_names)
data_positions = [[]] * len(file_names)
data_df = [[]] * len(file_names)

for file_idx in range(len(file_names)):
  df_ori = pd.read_csv(file_names[file_idx], skiprows=2)

  df = (
    df_ori
    .clean_names() # remove spacing and capitalization
    .drop(columns=['first_name', 'last_name', 'email_address']) # drop for privacy
    .dropna(subset=['company', 'position']) # drop missing values in company and position
    .to_datetime('connected_on', format='%d %b %Y')
  )
  #df.head()

  """## Simple EDA"""

  df['company'].value_counts().head(10).plot(kind="barh").invert_yaxis();

  df['position'].value_counts().head(10).plot(kind="barh").invert_yaxis();

  df['connected_on'].hist(xrot=35, bins=15);

  """### Remove freelance and self-employed titles"""

  pattern = "freelance|self-employed"
  df = df[~df['company'].str.contains(pattern, case=False)]

  """## Aggregate sum of connections for companies"""

  df_company = df['company'].value_counts().reset_index()
  df_company.columns = ['company', 'count']
  df_company = df_company.sort_values(by="count", ascending=False)
  df_company.head(10)

  """## Aggregate sum of connections for positions"""

  df_position = df['position'].value_counts().reset_index()
  df_position.columns = ['position', 'count']
  df_position = df_position.sort_values(by="count", ascending=False)
  df_position.head(10)

  ## Creating the network


  df_company_reduced = df_company.loc[df_company['count']>=3]

  df_position_reduced = df_position.loc[df_position['count']>=3]


  data_df[file_idx] = df
  data_company[file_idx] = df_company_reduced
  data_positions[file_idx] = df_position_reduced

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
#print("REPEATED COMPANIES: " + str(repeated_positions))
#print(data_company)

g = nx.Graph()
g.add_node('You') # intialize yourself as central
#print("HI")
# use iterrows tp iterate through the data frame

for idx in range(len(file_names)):
  df_company_reduced = data_company[idx]
  df_position_reduced = data_positions[idx]
  df = data_df[idx]

  for _, row in df_company_reduced.iterrows():
    #print("HI")
    # store company name and count
    company = row['company']
    count = row['count']

    title = f"<b>{company}</b> – {count}"
    positions = set([x for x in df[company == df['company']]['position']])
    positions = ''.join('<li>{}</li>'.format(x) for x in positions)

    position_list = f"<ul>{positions}</ul>"
    hover_info = title + position_list

    if company in repeated_company:
      g.add_node(company, size=count*2, title=hover_info, color=repeated_color_code)
    else:
      g.add_node(company, size=count*2, title=hover_info, color= colors[idx])
    g.add_edge('You', company, color='grey')

# generate the graph
nt = net.Network(height='700px', width='700px', bgcolor="black", font_color='white', notebook= True, cdn_resources='in_line')
nt.from_nx(g)
nt.hrepulsion()

nt.show('company_graph.html')
display(HTML('company_graph.html'))



# initialize graph
g = nx.Graph()
g.add_node('You') # intialize yourself as central

# use iterrows tp iterate through the data frame

for index in range(len(file_names)):
  df_company_reduced = data_company[index]
  df_position_reduced = data_positions[index]
  df = data_df[index]

  for _, row in df_position_reduced.iterrows():

    count = f"{row['count']}"
    position= row['position']

    if position in repeated_positions:
        #print("FOUND")
        g.add_node(position, size=count, color= repeated_color_code, title=count)
    else:
        g.add_node(position, size=count, color= colors[index], title=count)
    
    g.add_edge('You', position, color='grey')

# generate the graph
nt = net.Network(height='700px', width='700px', bgcolor="black", font_color='white', notebook= True, cdn_resources='in_line')
nt.from_nx(g)
nt.hrepulsion()
# more customization https://tinyurl.com/yf5lvvdm
nt.show('position_graph.html')
display(HTML('position_graph.html'))

