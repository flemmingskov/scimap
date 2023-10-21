'''
File: tool0_home.py
Author: Flemming Skov 
Purpose: Starting point and home for the application. Basic overview of production steps
and important and required data files and folder structure
Latest version: April 11 2021
'''

st.header("Science Mapping Home - rebuild version")
st.markdown('___')

exec(open("config.py").read())  # file with stored basic information - must be updated for a new project

# PROCESS and ABOUT EXPANDER
with st.expander("Overview of processes and available maps ..."):
    st.markdown(
        f"""       
        Select a process step from the drop-down menu in the sidebar. The following steps are available:

        ## PROCESS
        ##### Step 1: Import raw data from Web of Science 
        import of export text files from Web of Science
        ##### Step 2: Build a list of valid Web of Science (WoS) keywords
        create a list of unique keyword phrases from author keywords and keyword plus
        ##### Step 3: Process all keywords and update data base
        find and extract keyword phrases from title and abstract based on the list created in step 2
        #####  Step 4: Prepare node-edge files for network analysis
        build a co-occurrence matrix for keyword phrases
        ##### Step 5: Reduce dimensionality
        a force directed placement (FDP) is used to obtain a suitable spatial configuration
        ##### Step 6: Adjusting the layout
        expand, stretch and move the layout
        ##### Step 7: Prepare data for mapping
        export coordinates to sql-database for further use

        ## MAP TOOLS
        ##### Map 1: Maps distribution of papers in several categories 
    """)


add_empty_lines(expander_space)


# FOLDER AND FILES EXPANDER
with st.expander("Folders and files ..."):
    st.markdown(
        f"""       
        * All data should be kept in the main workspace
        * The work space must include a 'data' folder where the raw .txt imports from Web of Science are stored
        * In some cases, where a data overlay is needed more 'data' folders may be added. Use, e.g., 'data_overlay1', etc to name them
        * The program expects a 'figures' folder to store output

        #### Files
        This tool box mainly operates with two basis types of databases:

        * __'data.db'__ that contains imported (and later processed) bibliometric data from Web of Science
        * __'coor.db'__ that reference coordinates for all keywords in the specific landscape
        * __'map.db'__ that contain geo-referenced data for keywords, papers, persons and categories for the mapping
        
        Generally the 'data.db' and 'map.db' should be used for the reference map. If overlays are needed 
        (and to avoid confusion)  name them (e.g.) 'data_overlay.db' and 'map_overlay.db'. See also folder
        structure above
    """)

add_empty_lines(expander_space)

# CONFIG EXPANDER
with st.expander("Check of paths and files in project config.txt ..."):
    st.subheader("List of available workspaces in the config.py file")
    secondary_path = st.selectbox("workspace: ", list_secondary_paths)
    my_workspace = (primary_path + secondary_path)
    st.write('Full path: ', my_workspace)

    # show content of config.txt file in the chosen workspace
    config_file = my_workspace + 'config.txt'
    exec(open(config_file).read())  # file with stored basic information - must be updated for a new project
    st.markdown(
            f"""
            ##### Content of config.txt file
            * {default_data_db}
            * {default_coordinates_db}
            * {default_map_db}
            * {default_team_db}
            * {default_master_data}
            """) 
    st.write(' ')
    st.write('Edit the config.py file in a text editor to add more workspaces')

add_empty_lines(expander_space)