'''
File: tool5_graph.py
Author: Flemming Skov 
Purpose: Create a network layour based on the co-occurrence matrix
Latest version: November 12 2022
-- testing modularity in iGraph to cluster keywords as in Gephi --
'''

import igraph as ig

st.header("BASIC GRAPH LAYOUT")
st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information

# ABOUT EXPANDER
with st.expander("About ..."):
    st.subheader('Help:')
    st.markdown(
        f"""       
        Run Graph Layout using the 'Fruchtermann-Rheingold' algorithm in iGraph  
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
    data_depository = my_workspace + st.text_input('coordinate db: ', default_coordinates_db)
    st.success("db found: " + data_depository) if os.path.isfile(data_depository) else st.info("db does not exist")

    nodeFile = my_workspace + 'nodes.csv'
    edgeFile = my_workspace + 'edges.csv'

    for t in range(expander_space):
        st.write(' ')

# SETTINGS EXPANDER
with st.expander("Settings and controls ..."):
    
    max_iter= st.slider('Max number of iterations in graph layout: ', \
            min_value=100, max_value=1500, value=500, step=100, format=None, \
            key='max_iter_slider')

    resolution_param = st.slider('Resolution parameter: ', \
            min_value=0.5, max_value=2.00, value=1.0, step=0.05, format=None, \
            key='max_iter_slider')

    for t in range(expander_space):
        st.write(' ')

##  MAIN ACTION
st.markdown(' ')
st.subheader('CREATE GRAPH')
st.write(' ')
run_script =  st.button('Run script')

if run_script:
    begin_time = datetime.datetime.now()

    conn = sqlite3.connect(data_depository)

    try:
        with st.spinner('Graph layout in progress ...'):

        #  read node file
            node_labels = []
            with open(nodeFile, "r") as nodes_file:
                line = nodes_file.readline()    
                while line != "":      
                    strings = line.rstrip().split(",")
                    node_labels.append(str(strings[1]))
                    line = nodes_file.readline() 
            n_vertices = len(node_labels)        

        # read edge file
            edges = []
            weights = []
            with open(edgeFile, "r") as edges_file:
                line = edges_file.readline()    
                while line != "":      
                    strings = line.rstrip().split(",")
                    edges.append(((int(strings[0])-1), (int(strings[1])-1)))
                    weights.append(float(strings[2]))
                    line = edges_file.readline()

        # Create graph and add n vertices
            g = ig.Graph()
            g.add_vertices(n_vertices)

        # Add edges to the graph
            g.add_edges(edges)

        # Add weights to edges in the graph
            g.es['weight'] = weights
            g.vs["label"] = node_labels

        # Getting additional statistics
            p_degree = g.degree()
            p_weighted_degree = g.strength(mode="ALL", loops=True, weights=g.es['weight'])
            p_betweenness = g.betweenness()
            p_closeness = g.closeness()

            # cl1 = g.community_fastgreedy(weights=g.es['weight'])
            # k=10
            # p_modularity1 = cl1.as_clustering(k).membership

            # cl2 = g.community_multilevel(weights=g.es['weight'], return_levels=False)
            # p_modularity2 = cl2.membership

            #cl3 = g.community_leading_eigenvector(objective_function='modularity', weights=g.es['weight'], resolution_parameter=1.0, n_iterations=-1)
            cl3 = g.community_leiden(objective_function='modularity', weights=None, resolution_parameter=resolution_param, n_iterations=-1)
            p_modularity3 = cl3.membership

            num_values = len(set(p_modularity3))
            print('Number of clusters: ' + str(num_values))

            st.metric("Number of clusters", num_values, delta=None, delta_color="normal", help=None)

        # Creating the layout 
            random.seed(5)

            fg_weights_layout = g.layout_fruchterman_reingold(weights=g.es['weight'], niter=max_iter)
            x , y = np.array(fg_weights_layout.coords).T
            x_list=(x-x.min())/(x.max()-x.min())
            y_list=(y-y.min())/(y.max()-y.min())

            keyword_coordinates = pd.DataFrame({'keyword': node_labels, 'xcoor': x_list,
                                                'ycoor': y_list, 'degree': p_degree,
                                                'wdegree' : p_weighted_degree,
                                                'betweenness' : p_betweenness,
                                                'closeness' : p_closeness,
                                                'eigenvector' : p_modularity3
                                                })

            keyword_coordinates = keyword_coordinates.sort_values("wdegree", ascending=False)
            keyword_coordinates['distance'] = keyword_coordinates.apply(lambda row: math.hypot(row['xcoor'] \
                    - 0.5, row['ycoor'] - 0.5), axis=1)
            keyword_coordinates['bearing'] = keyword_coordinates.apply(lambda row: map_bearing(row['xcoor'], \
                    row['ycoor'], 0.5, 0.5), axis=1)
                
            keyword_coordinates.to_sql('keyword_raw_coordinates', conn, if_exists='replace')
            conn.close()   


    except Exception as e:
        print("Program Error: ")
        print(e)

    finally:
        st.success("Basic graph layout complete")
        print('... step 5 - basic graph layout constructed in: ' + str(datetime.datetime.now() - begin_time))
