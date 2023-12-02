
#!pip install pyjanitor pyvis --quiet
#!pip install --upgrade ipykernel





import pandas as pd
import janitor
import datetime

from IPython.core.display import display, HTML
from pyvis import network as net
import networkx as nx

df_ori = pd.read_csv("Connections.csv", skiprows=2)

df_ori.info()

"""## Data Cleaning"""

df = (
    df_ori
    .clean_names() # remove spacing and capitalization
    .drop(columns=['first_name', 'last_name', 'email_address']) # drop for privacy
    .dropna(subset=['company', 'position']) # drop missing values in company and position
    .to_datetime('connected_on', format='%d %b %Y')
  )
df.head()

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


# initialize graph
g = nx.Graph()
g.add_node('root') # intialize yourself as central
#print("HI")
# use iterrows tp iterate through the data frame



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

  g.add_node(company, size=count*2, title=hover_info, color='#3449eb')
  g.add_edge('root', company, color='grey')

# generate the graph
nt = net.Network(height='700px', width='700px', bgcolor="black", font_color='white', notebook= True, cdn_resources='in_line')
nt.from_nx(g)
nt.hrepulsion()

nt.show('company_graph.html')
display(HTML('company_graph.html'))



# initialize graph
g = nx.Graph()
g.add_node('root') # intialize yourself as central

# use iterrows tp iterate through the data frame
for _, row in df_position_reduced.iterrows():

  count = f"{row['count']}"
  position= row['position']

  g.add_node(position, size=count, color='#3449eb', title=count)
  g.add_edge('root', position, color='grey')

# generate the graph
nt = net.Network(height='700px', width='700px', bgcolor="black", font_color='white', notebook= True, cdn_resources='in_line')
nt.from_nx(g)
nt.hrepulsion()
# more customization https://tinyurl.com/yf5lvvdm
nt.show('position_graph.html')
display(HTML('position_graph.html'))

