'''
File: tool_main.py
Author: Flemming Skov 
Main streamlit/python file
Start app from a terminal window typing: "streamlit run 'path'/tool_main.py
Latest version: July 13 2021
'''

# Standard Library Imports
import os
import time
import datetime
import sqlite3
import platform
import logging
import itertools
import re
import math
import sys
import random

# Third-party Library Imports
import streamlit as st
import copy
import pandas as pd
import numpy as np
from nltk.stem import WordNetLemmatizer
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
from adjustText import adjust_text
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from matplotlib import ticker

# Styling
# FIXME Fix this later and get the right reference to seaborn styles
plt.style.use("seaborn-v0_8-whitegrid")

# Others
wnl = WordNetLemmatizer()

# Precompute the set of stopwords
stop_words_set = set(stopwords.words('english'))


exec(open("./apps/function_library.py").read())
     
# Define a dictionary to map tool names to their corresponding Python files
tools = {
    "Home": "./apps/tool0_home.py",
    "1 - import raw data": "./apps/tool1_import.py",
    "2 - create keyword vocabulary": "./apps/tool2_keyword_vocabulary.py",
    "3 - extract keywords from title": "./apps/tool3_keyword_extraction.py",
    "4 - build co-occurrence matrix": "./apps/tool4_prep_network.py",
    "5 - create network graph": "./apps/tool5_graph.py",
    "6 - adjust graph layout": "./apps/tool6_adjust_layout.py",
    "7 - prepare data for mapping": "./apps/tool7_prepare_map_db.py",
    "8 - create maps": "./apps/map1_distribution.py",
    "9 - keyword browser": "./apps/map2_keyword_browser.py",
    "10 - cluster maps": "./apps/map3_cluster_maps.py"
}
def main():
    exec(open("./apps/function_library.py").read())    

    st.sidebar.title("Tools for science mapping")
    st.sidebar.info("GitHub version 1.00 - October 21, 2023")
    
    # Menu layout
    page = st.sidebar.selectbox("Choose a tool page: ", list(tools.keys()))
    if page in tools:
        exec(open(tools[page]).read())
        exec(open("./apps/function_library.py").read())
    
    # # Menu layout
    # page = st.sidebar.selectbox("Choose a tool page: ",
    #          ["Home",
    #                 "1 - import raw data",
    #                 "2 - create keyword vocabulary",
    #                 "3 - extract keywords from title",
    #                 "4 - build co-occurrence matrix",
    #                 "5 - create network graph",
    #                 "6 - adjust graph layout",
    #                 "7 - prepare data for mapping",
    #                 "8 - create maps",
    #                 "9 - keyword browser",
    #                 "10 - cluster maps",
    #                 " ... not used ..."])

    # if page == "Home":
    #     exec(open("./apps/tool0_home.py").read())

    # elif page == "1 - import raw data":
    #     exec(open("./apps/tool1_import.py").read())  

    # elif page == "2 - create keyword vocabulary":
    #     exec(open("./apps/tool2_keyword_vocabulary.py").read())
          
    # elif page == "3 - extract keywords from title":
    #     exec(open("./apps/tool3_keyword_extraction.py").read())  

    # elif page == "4 - build co-occurrence matrix":
    #     exec(open("./apps/tool4_prep_network.py").read())

    # elif page == "5 - create network graph":
    #     exec(open("./apps/tool5_graph.py").read()) 
          
    # elif page == "6 - adjust graph layout":
    #     exec(open("./apps/tool6_adjust_layout.py").read()) 

    # elif page == "7 - prepare data for mapping":
    #     exec(open("./apps/tool7_prepare_map_db.py").read())

    # elif page == "8 - create maps":
    #     exec(open("./apps/map1_distribution.py").read())

    # elif page == "9 - keyword browser":
    #     exec(open("./apps/map2_keyword_browser.py").read())

    # elif page == "10 - cluster maps":
    #     exec(open("./apps/map3_cluster_maps.py").read())

    # # elif page == "slot not used ...":
    # #     exec(open("./apps/xxxx.py").read())      

    st.sidebar.markdown("   ")
    #st.sidebar.image("scimap.png", caption="Science map")
    st.sidebar.title("GitHub - code")
    st.sidebar.info(
        '''
        This a developing project and you are very welcome to *contribute* your 
        comments or questions to
        [GitHub](https://github.com/flemmingskov/scimap). 
        ''')
    st.sidebar.title("About")
    st.sidebar.info(
        """
        This app is maintained by Flemming Skov - 
        [AU Pure](https://pure.au.dk/portal/da/persons/flemming-skov(d16e357d-aa51-4bd3-ae16-9059110a3fe8).html).   
        """)
   
if __name__ == "__main__":
    main()