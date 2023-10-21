'''
File: tool4_prep_network.py
Author: Flemming Skov 
Purpose: Prepare nodes and edges (keywords and their connections) for the network analysis
that provides coordinates for each keyword.
Latest version: April 11 2021
'''

st.header("BUILD CO-OCCURRENCE MATRIX")
st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information

# ABOUT EXPANDER
with st.expander("About ..."):
    st.subheader('Help:')
    st.markdown(
        f"""       
        Prepare nodes file (for all keywords) and edge file (all co-occurrences of
        keywords). These files are used to layout keywords in a 2D space (step 5 in this process)
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

    node_file = my_workspace + 'nodes.csv'
    edge_file = my_workspace + 'edges.csv'

    for t in range(expander_space):
        st.write(' ')

# SETTINGS EXPANDER
with st.expander("Settings and controls ..."):
    low_cut = st.number_input('Mininum number of occurrences as focus or target', \
        min_value=1, max_value=100, value=2, key='low_cut_value')

    for t in range(expander_space):
        st.write(' ')


##  MAIN ACTION
st.markdown(' ')
st.subheader('CREATE MATRIX')
st.write(' ')
run_script =  st.button('Run script')

if run_script:
    
    try: 
        begin_time = datetime.datetime.now()

        # Read data from the 'keyword_collection' table, filtering out rows with empty 'kw_title'
        with sqlite3.connect(data_depository) as conn:
            dataframe_input = pd.read_sql_query('SELECT * FROM keyword_collection WHERE kw_title <> ""', conn).fillna('')
            # Read data from the 'vocabulary' table
            keyword_count = pd.read_sql_query('SELECT * FROM vocabulary', conn)

    except sqlite3.Error as e:
        print("SQLite Error:", e)
        
    try:
        with st.spinner('Processing node and edge files ...'):
            combined_list = []

            for index, row in dataframe_input.iterrows():
                keyword_str = ''       
                if row[2] != '':
                    keyword_str = row[2] + ';' +  row[3]
                else:
                    keyword_str = row[3]

                if keyword_str != []:
                    keyword_str = keyword_str + ';' + row[4]
                else:
                    keyword_str = row[[4]] 

                keyword_list = list(keyword_str.split(";"))
                keyword_list = list(set(keyword_list))
                combined_list.append(list(itertools.combinations(keyword_list, 2)))


            focus_list = []
            target_list = []
            for P in combined_list:
                for K in P:
                    focus_list.append(K[0])
                    target_list.append(K[1])

            dataframe_intermediate = pd.DataFrame({'focus': focus_list, 'target': target_list})

            dataframe_intermediate = pd.merge(dataframe_intermediate, keyword_count, left_on='focus', right_on='keyword', how='left')
            dataframe_intermediate = dataframe_intermediate[['focus', 'target', 'keyword_count']]
            dataframe_intermediate.columns = ["focus", "target", "focus_num"]

            dataframe_intermediate = pd.merge(dataframe_intermediate, keyword_count, left_on='target', right_on='keyword', how='left')
            dataframe_intermediate = dataframe_intermediate[['focus', 'target', 'focus_num', 'keyword_count']]
            dataframe_intermediate.columns = ["focus", "target", "focus_num", "target_num"]       
            
            dataframe_intermediate = dataframe_intermediate.loc[(dataframe_intermediate['focus_num'] >= low_cut) & (dataframe_intermediate['target_num'] >= low_cut)]
            dataframe_intermediate.reset_index(inplace = True, drop = True)

            dataframe_intermediate = dataframe_intermediate.dropna()[['focus', 'target']]

            dataframe_raw = ''
            dataframe_A1 = ''

            dataframe_A1 = dataframe_intermediate.iloc[:]
            dataframe_A1.columns = ['kw1', 'kw2']

            dataframe_A1L = dataframe_A1['kw1']
            dataframe_A1L.columns = ['kw']
            dataframe_A1R = dataframe_A1['kw2']
            dataframe_A1R.columns = ['kw']
            dataframe_stacked = pd.concat([dataframe_A1L, dataframe_A1R], axis=0)
            dataframe_stacked = pd.DataFrame(dataframe_stacked)
            dataframe_stacked.columns = ['kw']

            uniqs = pd.unique(dataframe_stacked.kw.ravel())

            nodes = pd.DataFrame(uniqs)
            nodes.columns = ['label']
            nodes['ID'] = nodes.index + 1
            nodes = nodes[["ID", "label"]]

            edges = pd.merge(left=dataframe_A1, right=nodes, how='left', left_on='kw1',
                            right_on='label')
            edges = pd.merge(left=edges, right=nodes, how='left', left_on='kw2',
                            right_on='label')
            edges = edges[["ID_x", "ID_y"]]
            edges.columns = ['source', 'target']
            edges['weight'] = 1

            ## NEW FUNCTIONALITY HERE
            from collections import Counter 
            edge_list = []
            
            for index, row in edges.iterrows():
                my_tup = (row[0], row[1])
                edge_list.append(my_tup)
            
            edge_list_sort = list(([ tuple(sorted(t)) for t in edge_list ]))
            # Getting count 
            dict = Counter([tuple(i) for i in edge_list_sort]) 
        
            # Creating pandas dataframe 
            edge_list_weight = pd.DataFrame(data ={'list': list(dict.keys()),'count': list(dict.values())}) 
            
            source_list = []
            target_list = []
            weight_list = []
            for index, row in edge_list_weight.iterrows():
                source_list.append(row[0][0])
                target_list.append(row[0][1])
                weight_list.append(row[1])
                
            edges_new = ((pd.DataFrame({'source': source_list, 'target': target_list,
                        'weight': weight_list})[:])
                        [['source', 'target', 'weight']] )
        
            nodes.to_csv(node_file, sep=',', index=False, header=False)
            edges_new.to_csv(edge_file, sep=',', index=False, header=False)


            # Showing metrics
            col1, col2 = st.columns(2)
            col1.metric("Number of nodes", len(nodes))
            col2.metric("Number of edges", len(edges_new))

    except Exception as e:
        print("Program Error: ")
        print(e)

    finally:
        st.success("Data for graph generation created (node- and edge files))")
        print('... step 4 - node and edge files prepared for graph layout in: ' + str(datetime.datetime.now() - begin_time))