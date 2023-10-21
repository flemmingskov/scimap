'''
File: tool3_keyword_extraction.py
Author: Flemming Skov 
Purpose: Find and extract keywords in title or abstract using the keyword vocabulary
Latest version: May 22 2022
'''

st.header("CLEAN AND EXTRACT KEYWORDS")
st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information

# ABOUT EXPANDER
with st.expander("About ..."):
    st.subheader('Help:')
    st.markdown(
        f"""       
        The purpose of this tool is to clean keywords or keyword phrases from the raw
        import data base and create a new table with four columns with processed keywords 
        for each WoS record:
        * kw1_clean (original author supplied keywords)
        * kw2_clean (keywords Plus)
        * kw_title - list of keywords from title
        * kw_abstr - list of keywords from abstract  
    """)

    for t in range(expander_space):
        st.write(' ')

# WORKSPACE & FILE EXPANDER
with st.expander("Workspace and data bases ..."):
    secondary_path = st.selectbox("Path to primary workspace: ", list_secondary_paths)
    my_workspace = (primary_path + secondary_path)

    ws_config_file = my_workspace + 'config.txt'
    exec(open(ws_config_file).read())

    # open connection to map database
    data_depository = my_workspace + st.text_input('data base: ', default_data_db)

    st.success("db found: " + data_depository) if os.path.isfile(data_depository) else st.info("db does not exist")

    for t in range(expander_space):
        st.write(' ')

# SETTINGS EXPANDER
with st.expander("Settings and controls ..."):
    st.markdown(
        f"""       
        Please, note: running the script will replace existing data in table _'keyword_collection'_
        """)

    st.write("Include keywords from:")
    run_keywords = st.checkbox('Web of Science', value=True, key='runKeywords')
    run_title = st.checkbox('Title', value=False, key='runTitle')
    run_abstract = st.checkbox('Abstract', value=False, key='runKAbstract')
    low_cut = st.number_input('Mininum number of occurrences in vocabulary', \
        min_value=1, max_value=125, value=2, key='minVocValue')

    for t in range(expander_space):
        st.write(' ')


##  MAIN ACTION
st.markdown(' ')
st.subheader('EXTRACT KEYWORDS')
st.write(' ')
run_script =  st.button('Run script')

if run_script:
    c
    begin_time = datetime.datetime.now()

    conn = sqlite3.connect(data_depository)
    data_df = pd.read_sql_query('select * from wosdata;', conn).fillna('')
    links_df = pd.read_sql_query('select * from links;', conn)

    keywords_approved = pd.read_sql_query('select * from vocabulary;', conn)
    keywords_approved = keywords_approved[keywords_approved['keyword_count'] >= low_cut]
    keywords_approved = keywords_approved['keyword'].tolist()

    search_string = """(links_df.category != 'dummyCriteria')"""
    subset = (links_df.loc[eval(search_string), ['wosid']]
                    .drop_duplicates(['wosid']))
    data_to_be_processed = (pd.merge(subset, data_df, on='wosid', how='inner')[['authors', 'title', 
                    'kw1', 'kw2', 'abstr', 'inst', 'email', 'autID', 'funding', 
                    'cites', 'journal', 'year', 'wos_sub_cat1', 'wos_sub_cat2', 
                    'wosid', 'time_stamp']]  )

    # set to supress warning of chained assigment - not recommended, but looks nicer in output ;)                
    pd.set_option("mode.chained_assignment", None)

    try:
        with st.spinner('Processing and extracting keywords ...'):
            clean_list = []
            data_to_be_processed['kw1_clean'] = ''
            data_to_be_processed['kw2_clean'] = ''
            data_to_be_processed['kw_title'] = ''
            data_to_be_processed['kw_abst'] = ''

            for index, row in data_to_be_processed.iterrows(): 
            

                # cleaning regular keywords
                if run_keywords:
                    with st.spinner('processing regular keywords ...'):
                        current_record = row[14]
                        keyword_list = row[2]
                        concat_clean = ''
                        for kw in keyword_list.split(";"):
                            cleaned_keyword = clean_keyword(kw, synonyms)
                            if concat_clean == '':
                                concat_clean = cleaned_keyword
                            else:
                                concat_clean = concat_clean + ';' + cleaned_keyword
                        data_to_be_processed.loc[index,['kw1_clean']] = concat_clean  

                        ## keywords plus from Web of Science
                        keyword_list = row[3]
                        concat_clean = ''
                        for kw in keyword_list.split(";"):
                            cleaned_keyword = clean_keyword(kw, synonyms)
                            if concat_clean == '':
                                concat_clean = cleaned_keyword
                            else:
                                concat_clean = concat_clean + ';' + cleaned_keyword
                        data_to_be_processed.loc[index,['kw2_clean']] = concat_clean

                # extracting keywords from title
                if run_title:
                    title_text = row[1]
                    keywords_in_title = extract_keywords_from_text(title_text, keywords_approved, synonyms) 
                    data_to_be_processed.loc[index,['kw_title']] = keywords_in_title
        
                # extracting keywords from abstract
                if run_abstract:
                    abstract_text = row[4]
                    if abstract_text != '':
                        keywords_in_abstract = extract_keywords_from_text(abstract_text, keywords_approved, synonyms)
                        data_to_be_processed.loc[index,['kw_abst']] = keywords_in_abstract
                    else:
                        data_to_be_processed.loc[index,['kw_abst']] = ''

        processed_data = data_to_be_processed[['wosid', 'kw1_clean', 'kw2_clean', 'kw_title', 'kw_abst', 'year']]

        processed_data[["year"]] = processed_data[["year"]].apply(pd.to_numeric)
        processed_data = processed_data[processed_data['year'].notna()]
        st.dataframe(processed_data)   

        processed_data.to_sql('keyword_collection', conn, if_exists='replace')
        conn.close()    

    except Exception as e:
        print("Program Error: ")
        print('Index number: ' + str(index) + '  WoS-ID: ' + str(current_record))
        print(str(concat_clean))
        print(e)

    finally:
        st.success("Keywords extracted from paper titles (and/or abstracts)")
        print('... step 3 - keywords processed (and extracted from title (or/and abstract)) in: ' + str(datetime.datetime.now() - begin_time))


# NOTES AND COMMENTARIES #####################################################
'''
Problem found on July 3, 2020 when importing records from Web of Science. 5-6 records
(Spanish) contained '(sic)(sic)' and similar meaningless keywords. They caused
the script to stop. Bug not fixed, but the error handler now prints the index number of the
record that failed to help remove the bugs in the raw text files
'''