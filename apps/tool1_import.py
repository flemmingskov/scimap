'''
File: tool1_import.py
Author: Flemming Skov 
Purpose: Import raw data to a pandas dataframes, basic clean and store in sql3 format
Latest version: May 23 2022
'''

st.header("IMPORT RAW DATA")
st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information - must be updated for a new project
# various fixed settings 
(label_name, faculty_name, discipline_name, unit_name, person_name) \
        = ('biol', 'Sciences', 'Biology', '', '')

# ABOUT EXPANDER
with st.expander("About ..."):
    st.subheader('Help:')
    st.markdown(
        f"""       
        Use this tool to import data from Web of Science. When a set of records has been found in Web of Science, use the 'Export ...' 
        function and select 'Other File Formats'.
        It is only possible to export up to 500 records a time and the process may have to be repeated. Use the 'records from .. to ..'
        to select records. Use 'Full Record' in 'Record Content' and File Format 'Tab-delimited'. Copy export .txt files
        to 'Data' folder in the chosen workspace.

        * Check the folder hierarchy: The primary folder (workspace) should contain a
        'Data' folder to hold the imported .txt files from Web of Science
        * Any number of .txt files in the 'Data' folder will be imported when pressing 'Run'
        * The import will replace existing tables 'wosdata' and 'links'  
    """)

    add_empty_lines(expander_space)

# WORKSPACE & FILE EXPANDER
with st.expander("Workspace and data bases ..."):
    secondary_path = st.selectbox("Path to primary workspace: ", list_secondary_paths)
    my_workspace = (primary_path + secondary_path)

    ws_config_file = my_workspace + 'config.txt'
    exec(open(ws_config_file).read())

    # open connection to map database
    data_depository_path = my_workspace + st.text_input('data base: ', default_data_db)

    st.success("db found: " + data_depository_path) if os.path.isfile(data_depository_path) else st.info("db does not exist")

    add_empty_lines(expander_space)

##  MAIN ACTION
st.markdown(' ')
st.subheader('IMPORT WOS DATA')
st.write(' ')
run_script =  st.button('Run script')

if run_script:
    begin_time = datetime.datetime.now()

    data_connection = sqlite3.connect(data_depository_path)
    streamlit_directory = os.getcwd()
    time_stamp = datetime.datetime.now().strftime('(%Y,%b,%d)')  # time stamp
    
    try:
        with st.spinner('Importing ...'):
               
            imported_data_df = pd.DataFrame()

            # step 1 - open and import file content(s) to new dataframe
            os.chdir(my_workspace+'data/')
            for filename in os.listdir():
                if filename.endswith('.txt'):
                    print(' .. importing: ' + filename)
                    
                    
                    columnames = []
                    for i in range(0, 71):    #alternative (0 69)
                        columnames.append(str(i))

                    with open(filename) as f:
                        firstline = f.readline().rstrip()
                        split_string = firstline.split("\t")
                        index_AU = split_string.index('AU')
                        index_TI = split_string.index('TI')
                        index_DE = split_string.index('DE')
                        index_ID = split_string.index('ID')
                        index_AB = split_string.index('AB')
                        index_C1 = split_string.index('C1')
                        index_EM = split_string.index('EM')
                        index_RI = split_string.index('RI')
                        index_FU = split_string.index('FU')
                        index_Z9 = split_string.index('Z9')
                        index_SO = split_string.index('SO')
                        index_PY = split_string.index('PY')
                        index_WC = split_string.index('WC')
                        index_SC = split_string.index('SC')
                        index_UT = split_string.index('UT')
                 
                    wosIn_df = pd.read_csv(filename, names=columnames,
                                        index_col=False,
                                        delimiter='\t',
                                        skiprows=1)
                                 
                    wosIn_df = wosIn_df[wosIn_df.columns[[index_AU, index_TI, index_DE, index_ID, index_AB, index_C1, index_EM, index_RI,
                                                        index_FU, index_Z9, index_SO, index_PY, index_WC, index_SC, index_UT]]]

                
                    wosIn_df.replace(r'\s+', np.nan, regex=True).replace('', np.nan)
                    wosIn_df = wosIn_df.fillna('')
                    wosIn_df[100] = time_stamp    # New column with time stamp (today)
                    wosIn_df.columns = ['authors', 'title', 'kw1', 'kw2', 'abstr',
                                        'inst', 'email', 'autID', 'funding', 'cites',
                                        'journal', 'year', 'wos_sub_cat1',
                                        'wos_sub_cat2', 'wosid', 'time_stamp']
                    imported_data_df = pd.concat([imported_data_df, wosIn_df])
                

            imported_data_df = imported_data_df.drop_duplicates(subset='wosid', keep='last')

            imported_data_df[["cites", "year"]] = imported_data_df[["cites", "year"]].apply(pd.to_numeric, \
                    errors='coerce')

            imported_data_df.loc[imported_data_df['year'] < 1920, 'year'] = np.nan
            imported_data_df = imported_data_df.dropna(subset=['year', 'wosid'])

            imported_data_df['year'] = imported_data_df.year.astype(int)
            imported_data_df['cites'] = imported_data_df.cites.astype(int)

            os.chdir(streamlit_directory)  # resetting directory to streamlit-base

            # step 2 - linking unique categories to WoS IDs        
            wos_list, year_list, cat_list, cite_list, faculty_list, discipline_list, unit_lilst, \
                    person_list, label_list, email_list, funding_list = ([] for i in range(11))

            for row in imported_data_df.itertuples(index=False):
                wosid = row[14]
                yr = row[11]
                cat1list = row[12]
                cat2list = row[13]
                cites = row[9]

                # set to cat1list or cat2list (specific/general categories)
                for cat in cat1list.split(";"):
                    if cat != "":
                        # cat = cat.replace(" ", " ")
                        cat = cat.lstrip()
                        wos_list.append(wosid)
                        year_list.append(yr)
                        cat_list.append(cat)
                        cite_list.append(cites)
                        faculty_list.append(faculty_name)
                        discipline_list.append(discipline_name)
                        unit_lilst.append(unit_name)
                        person_list.append(person_name)
                        label_list.append(label_name)

            # create Pandas dataframe for link between WoS_id and categories
            links_df = pd.DataFrame({'wosid': wos_list, 'year': year_list,
                                    'category': cat_list, 'cites': cite_list,
                                    'faculty': faculty_list,
                                    'discipline': discipline_list, 'unit': unit_lilst,
                                    'person': person_list, 'label': label_list})
            links_df = links_df[1:]
            links_df = links_df[['wosid', 'year', 'cites', 'category', 'faculty',
                                'discipline', 'unit', 'person', 'label']]
            dep_links_df = links_df
            dep_links_df = dep_links_df.drop_duplicates(keep='last')

            # Step 3 - save data frames in SQLite db
            imported_data_df.to_sql('wosdata', data_connection, if_exists='replace')
            dep_links_df.to_sql('links', data_connection, if_exists='replace')
            data_connection.close()

            imported_data_df = imported_data_df.reset_index(drop=True)

        st.markdown(
        f"""       
        Number of unique records imported: {str(len(imported_data_df))}
        Number of links: {str(len(dep_links_df))}   
        """)

        st.dataframe(imported_data_df)

    except Exception as e:
        print("Program Error: ")
        print(e)

    finally:
        st.success("Web of Science records imported successfully")
        print('... step 1 - imported WoS records to data base: ' + str(datetime.datetime.now() - begin_time))

# Notes

'''

'''