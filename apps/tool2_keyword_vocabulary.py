'''
File: tool2_keyword_vocabulary.py
Author: Flemming Skov 
Purpose: Create a list of unique keywords from author keywords and keywords Plus
Latest version: April 11 2021
'''

st.header("CREATE KEYWORD VOCABULARY")
st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information

# ABOUT EXPANDER
with st.expander("About ..."):
    st.subheader('Help:')
    st.markdown(
        f"""       
        Use this tool to generate a list of unique keywords from 'author keywords'
        and 'keywords Plus' imported to the SQLite data base.
        The list of keywords (and how often they occur)  will be as a table in the data base.
        This keyword vocabulary will be used to extract keywords from title and abstract.
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


##  MAIN ACTION
st.markdown(' ')
st.subheader('CREATE KEYWORD VOCABULARY')
st.write('  ')
run_script =  st.button('Run script')

if run_script:
    begin_time = datetime.datetime.now()

    conn = sqlite3.connect(data_depository)
    data_df = pd.read_sql_query('select * from wosdata;', conn).fillna('')
    links_df = pd.read_sql_query('select * from links;', conn)

    searchCriteria = """(links_df.category != 'dummyCriteria')"""   ## If necessary to select subset
    subset = (links_df.loc[eval(searchCriteria), ['wosid']]
                    .drop_duplicates(['wosid']))
    dataIn = (pd.merge(subset, data_df, on='wosid', how='inner')[['authors', 'title', 
                    'kw1', 'kw2', 'abstr', 'inst', 'email', 'autID', 'funding', 
                    'cites', 'journal', 'year', 'wos_sub_cat1', 'wos_sub_cat2', 
                    'wosid', 'time_stamp']]  )

    try:
        with st.spinner('Preparing vocabulary ...'):

            synonyms = import_synonyms()
            (wosid_list, year_list, orig_list, clean_list, comb_list, keyword_list) = \
                ([], [], [], [], [], [])
            
            for row in dataIn.itertuples(index=False):
                concat_clean = []

                if row[2] != '':
                    keyword_list = row[2] + ';' +  row[3]
                else:
                    keyword_list = row[3]     

                for kw in keyword_list.split(";"):  # iterate over all keywords in one article
                    cleaned_keyword = clean_keyword(kw)
                    wosid_list.append(row[14])
                    year_list.append(row[11])
                    orig_list.append(kw)
                    clean_list.append(cleaned_keyword)
                    concat_clean.append(cleaned_keyword)
                comb_list.append(list(itertools.combinations(concat_clean, 2)))                

            raw_keyword_list = ((pd.DataFrame({'keyword': clean_list, 'orgKw': orig_list,
                        'year': year_list, 'wosid': wosid_list})[:])
                        [['wosid', 'year', 'keyword', 'orgKw']] )

            keyword_count = pd.DataFrame(raw_keyword_list['keyword'].value_counts())
            keyword_count['label'] = keyword_count.index   # create new column and copy index to it
            keyword_count.columns = ["keyword_count", "keyword"]

            ## LIST of keywords to erase from vocabulary
            for delete_kw in ['biogeography', 'pattern', 'north', 'northern', 'south', 'southern', 
                                'east', 'eastern', 'west', 'western']:
                keyword_count.drop(keyword_count.loc[keyword_count['keyword']==delete_kw].index, inplace=True)
                
            keyword_count = keyword_count.reset_index(drop=True)
            total_count = len(keyword_count)
            ones = total_count - len(keyword_count[keyword_count['keyword_count'] == 1])
            twos = total_count - len(keyword_count[keyword_count['keyword_count'] <= 2])

            st.markdown(
            f"""Total number of keywords is {total_count}. Number of keywords with two or 
            more occurrences: {ones}. Number of keywords with three or 
            more occurrences: {twos}""") 

            st.dataframe(keyword_count)

            keyword_count.to_sql('vocabulary', conn, if_exists='replace')
            conn.close()     

    except Exception as e:
        print("Program Error: ")
        print(e)

    finally:
        st.success("Basic vocabulary created")
        print('... step 2 - vocabulary of keywords created in: ' + str(datetime.datetime.now() - begin_time))