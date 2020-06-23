#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datetime import datetime
from datetime import datetime
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 500)


# In[2]:


import seaborn as sns
import matplotlib.pyplot as plt
#%matplotlib inline


# In[3]:


import chart_studio.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs,init_notebook_mode,plot,iplot
init_notebook_mode(connected=True)


# # Scrap Data From The Github Site (Link Below)

# Github Data API - https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.json
# Github Repository of Police Brutality - https://github.com/2020PB/police-brutality/blob/master/README.md

# In[4]:


pb_data_raw = pd.read_json(r'https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.json')


# # Set data up into proper matrix format 

# In[5]:


# creates a dictionary from the List of Data Frame Names (Keys) and the Data Frame Files (Values) themselves
dict_of_pb_dfs = {}

for pb_record_idex_num in range(0,len(pb_data_raw['data'])): 
    globals()["pb_df_{}".format(pb_record_idex_num)]  = pd.DataFrame(pb_data_raw['data'][pb_record_idex_num])
    dict_of_pb_dfs["pb_df_{}".format(pb_record_idex_num)] = globals()["pb_df_{}".format(pb_record_idex_num)]
    
# Reduces the record numbers to 1 per incident in each data frame
for pb_df in dict_of_pb_dfs.keys():
    num_count = len(dict_of_pb_dfs[pb_df])-1
    while num_count > 0:
        dict_of_pb_dfs[pb_df].drop(num_count, inplace = True)
        num_count -= 1
        
# Concatenate the individual data frames into one dataframe with all the incident data (one link/record per incident)
list_of_values = list(dict_of_pb_dfs.values())
pd_consolidated = pd.concat(list_of_values, sort = True)
pd_consolidated['incident_value'] = 1


# # Geographical Plotting

# In[6]:


# create a ditionary of State Names and Abbreviations
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'dc',
    'Washington DC': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'   
}
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

date_text = '2020-06-23'
pd_consolidated = pd_consolidated[pd_consolidated['date'] == date_text]
pd_consolidated_pre_zeros = pd_consolidated

pb_state_list = np.array(list(pd_consolidated['state']))
blank_state = {}
for state in us_state_abbrev.keys():
    #print(state)
    
    if state in pb_state_list:
        #print('In List\n')
        pass
    else:
        #print('\tNOT IN LIST')
        blank_state[state] = {}
        record_input = pd.DataFrame(index = [0],columns = ['city','date','date_text','edit_at', 'id', 'links','name','state','incident_value'])
        record_input.xs(0)['state']=state
        record_input.xs(0)['incident_value']=0
        globals()["{}".format(state)]  = record_input
        blank_state["{}".format(state)] = globals()["{}".format(state)]
        pd_consolidated = pd.concat([blank_state['{}'.format(state)],pd_consolidated])


# In[7]:


by_state = pd_consolidated.groupby('state')
by_state_sum_incidents = by_state.sum()

pb_state_abbreviation_code_list = []
for state in by_state_sum_incidents['incident_value'].index:
    if state in list(us_state_abbrev.keys()):
        pb_state_abbreviation_code_list.append(us_state_abbrev[state])
#     elif state == 'Washington DC':
#         pb_state_abbreviation_code_list.append("DC")
    else:
        pb_state_abbreviation_code_list.append("Unknown Location")

        
# Set up dictionary for the Plotly Map Text      
dict_of_incident_names = {}

for state in by_state_sum_incidents['incident_value'].keys():
    #print(state)
    dict_of_incident_names[state] = {}
    pb_query = pd_consolidated['state'] == state
    #print(pd_consolidated[pb_query]['links'])
    dict_of_incident_names[state] = pd_consolidated[pb_query]['name']

array_pb_incident_names = np.array(list(dict_of_incident_names.values()))


# Set up data for Plotly Map
data = dict(type = 'choropleth',
           colorscale = 'greys',
           locations = pb_state_abbreviation_code_list,
           locationmode = 'USA-states',
           z = by_state_sum_incidents['incident_value'].values,
           text = np.array(list(pd_consolidated['state'])),
            hovertext = array_pb_incident_names,
            hoverinfo = "all",
            #hovertemplate = "%{hovertext} <extra>%{location} <br> Number of Incidents: %{z}</extra>",
            #hovertemplate = "https://github.com/2020PB/police-brutality/blob/master/reports/%{text}.md <extra>%{location} - Number of Incidents: %{z} </extra>",
            #hovertemplate = "<a href=\"https://github.com/2020PB/police-brutality/blob/master/reports/%{text}.md\">link to github</a> <extra>%{location} - Number of Incidents: %{z} </extra>",
            #hovertemplate = "%{location} <br> Number of Incidents: %{z} <extra>%{hovertext}</extra>",
            #hovertemplate = "%{location} <br> Number of Incidents: %{z} <extra>https://github.com/2020PB/police-brutality/blob/master/reports/%{text}.md</extra>",
            hovertemplate = "%{location} <br> Number of Incidents: %{z} <extra></extra>",
            marker = dict(line = dict(color = 'rgb(65,65,65)',width = 1)),
           colorbar = {'title': 'Police Brutality Incident Counts'}
           )
#Title Variable
by_date = pd_consolidated.groupby('date')
by_date_sum_incidents = by_date.sum()

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

title_of_layout = "2020 Police Brutality: {} Incidents Captured on Video<br>Data from {}<br>Date Created: {} MST".format(len(pd_consolidated_pre_zeros),date_text,dt_string)

# Set up Layout for Plotly Map
layout = dict(title = title_of_layout,
             geo = dict(scope = 'usa'))

# Call Plotly Map and set it as a variable
choromap_pb2020 = go.Figure(data = [data], layout = layout)

choromap_pb2020.update_layout(
    hoverlabel=dict(
        bgcolor="black", 
        font_size=12, 
        font_family="Rockwell"
    )
)
# Save html
choromap_pb2020.write_html(r"C:\Users\cdwhi\Documents\Python\My_Code\Police_Brutality_2020\PB_2020_Choropleth_Map_by_State_Count_20200623\index.html")

# Plot the Map
#plot(choromap_pb2020)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




