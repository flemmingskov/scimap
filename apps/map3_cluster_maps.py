'''
File: map1_distribution.py
Author: Flemming Skov 
Purpose: Maps the density of papers for individual subject categories, keywords, researchers
and institutions . 
Latest version: July 14, 2022
'''

st.header("DISTRIBUTION MAPPING")
st.markdown('___')


#st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information

@st.cache(suppress_st_warning=True)
def import_data(overlay_db, table_select):
    connection_db = sqlite3.connect(overlay_db)
    table_to_import = pd.read_sql_query('select * from ' + table_select + ';', connection_db)
    return table_to_import 

# ABOUT EXPANDER
with st.expander("About ..."):
    st.subheader('Help:')
    st.markdown(
        f"""       
        This tools maps the distribution of Web of Science subject categories,
        institutions, individual researchers in the selected scientific reference landscape.
        Use the radio-buttons above to select the focus of the map.
        Use the drop-down menu in 'Filters' section to select which item to map (and set the time frame). 
        All map settings are controlled from the from the 'Map & graphic settings' section. The section
        "Workspace and data bases" shows the available workspaces and sqlite databased (this information is
        stored in the config.py file)

    """)

    for t in range(expander_space):
        st.write(' ')


 

    column_identifier = 'HUMANS'
    data_shade_center_table = 'clustC'
    data_shade_points_table = 'clustD'





# WORKSPACE & FILE EXPANDER
with st.expander("Workspace and data bases ..."):
    secondary_path = st.selectbox("Path to primary workspace: ", list_secondary_paths)
    my_workspace = (primary_path + secondary_path)

    ws_config_file = my_workspace + 'config.txt'
    exec(open(ws_config_file).read())

    # open connection to map database
    list_clusters =  ['THEMES.db', 'METHODS.db', 'HUMANS.db']
    overlay_db = my_workspace + st.selectbox('Select map data base: ', list_clusters)  
    st.success("db found: " + overlay_db) if os.path.isfile(overlay_db) \
        else st.info("db does not exist")

    for t in range(expander_space):
        st.write(' ')

    connection_db = sqlite3.connect(overlay_db)

# MAP & GRAPHIC SETTINGS EXPANDER
with st.expander("Map & graphic settings ... ..."):
    st.markdown(
        f"""       
        Show points: a dot for each individual paper; Adjust
        labels: use label placement algorithm (time consuming with many labels).  
    """) 

    # fixed variables
    fig_side=20
    cat_txt_transp = 0.95
    cat_txt_col = 'black'
    marker_size = 7
    marker_transparence=0.95

    # adjustable variables (in layout)
    col1, col2 = st.columns([2, 2])

    shade_on = col1.checkbox('Use graduated shading', value=True, key='check_shade')
    contour_on = col2.checkbox('Use contour lines', value=False, key='check_contours')

    use_overlay = col1.checkbox("Show point cloud", value=False, key='overlay_checkbox')
    show_title = col2.checkbox("Show plot title", value=True, key='show_title_checkbox')

    show_captions = col1.checkbox("Show text labels", value=False, key='showlabels')
    adjust_labels = col2.checkbox("Adjust text labels", value=False, key='adjustlabels_checkbox')

    number_of_labels = col1.slider('Number of text labels (from them most common):', 0, 300, 15, 1, \
        key='number_of_labels')
    number_of_levels = col2.slider('Number of contour lines:', 2, 50, 20, 1, \
        key='number_of_levels')
    
    shade_color = col1.text_input('Shading color', value='blue', key='shade_color', \
        type='default')
    shade_alpha = col2.number_input('Shading transparency', min_value=0.05, \
        max_value=1.0, value=0.45, key='shade_alpha_slider')

    marker_color = col1.text_input('Marker color', value='red', key='marker_color', type='default')
    low_thresh = col2.number_input('Lower threshold', min_value=0.001, \
        max_value=0.95, value=0.05, key='low_thresh')

    cat_txt_min = col1.number_input('label text min', min_value=6, max_value=30, value=9, \
        step=1, key='text_min')
    cat_txt_max = col2.number_input('label text max', min_value=10, max_value=40, value=14, \
        step=1, key='text_max')

    crop_ymin = col1.number_input('y min', min_value=0.0, max_value=1.0, value=0.0, \
        step=0.05, key='cropUL')
    crop_ymax = col2.number_input('y max', min_value=0.0, max_value=1.0, value=1.0, \
        step=0.05, key='cropUR')
    crop_xmin = col1.number_input('x min', min_value=0.0, max_value=1.0, value=0.0, \
        step=0.05, key='cropLL')
    crop_xmax = col2.number_input('x max', min_value=0.0, max_value=1.0, value=1.0, \
        step=0.05, key='cropLR')

    for t in range(expander_space):
        st.write(' ')



# FILTER EXPANDER
with st.expander("Filters ..."):
    category_select = " "
    data_shade_center = import_data(overlay_db, data_shade_center_table)
    #data_shade_center = data_shade_center.sort_values(by=sort_column, ascending=0)
    data_shade_center = data_shade_center.reset_index(drop=True)
    top10 =data_shade_center[:175]

    category_list = top10[column_identifier].to_numpy().tolist()
    category_list.append("All papers")
    category_select = st.selectbox("Select a researcher to map", category_list)
    export_file_suggested_name = category_select.lower().replace(' ', '').replace(',', '') + '.png'

    col1, col2 = st.columns([2, 2])
    start_year = col1.number_input('Choose records from year:', min_value=1965, max_value=2022, value=1980, \
        step=1 , format=None, key='start_y', help=None)
    steps_year = col2.number_input('.. plus time span in years', min_value=0, max_value=75, value=45, \
        step=5, format=None, key='step_y', help=None)
    end_year = start_year + steps_year

    # Import data tables
    # data_papers = import_data(overlay_db, data_papers_table)
    # data_papers = data_papers[((data_papers['year']>= start_year) & \
    #     (data_papers['year']<= end_year))]
    # data_papers = data_papers.dropna()



    # import density data by year
    data_shade_points = import_data(overlay_db, data_shade_points_table)
    data_shade_points = data_shade_points[((data_shade_points['year']>= start_year) & \
            (data_shade_points['year']<= end_year))]


    # preparing data
    if category_select != 'All papers':
        selected_category = data_shade_points[data_shade_points[column_identifier] == category_select]
        selected_category.sort_values(by='year', ascending=0)
        selected_category = selected_category.drop_duplicates(subset='wosid', keep='last')
    else:
        selected_category = data_shade_points
        selected_category.sort_values(by='year', ascending=0)
        selected_category = selected_category.drop_duplicates(subset='wosid', keep='last')

    
    # showing data (controls which data to show)
    data_to_select = selected_category[['wosid', 'xcoor', 'ycoor', 'year']]
#    data_to_inform = data_papers[['wosid', 'title', 'authors', 'cites']]
    data_to_show = data_to_select
    # data_to_show = pd.merge(data_to_select, data_to_inform)
    # data_to_show = data_to_show[['authors', 'title', 'year', 'cites', 'xcoor', 'ycoor']]

    st.markdown(
        f"""       
        {category_select} has {str(len(selected_category.index))} \
        papers out of {str(len(data_shade_points.drop_duplicates(subset='wosid')))} (from {start_year} to {end_year} )""")

##  MAIN ACTION
st.markdown(' ')
st.subheader('MAPS & DATA')

# determining size of label fontt
# label_text = []
# label_size1 = []
# for woscat in range(0,number_of_labels):
#     label_text.append(data_shade_center.loc[woscat, column_identifier])
#     # label_size1.append(data_shade_center.loc[woscat, sort_column])

# old_max = max(label_size1)
# old_min = min(label_size1)
# old_range = (old_max - old_min)  
# new_range = (cat_txt_max - cat_txt_min)

# label_size = []
# for l in label_size1:
#     old_value = l
#     new_value = (((old_value - old_min) * new_range) / old_range) + cat_txt_min
#     label_size.append(new_value)

# layout and outline
sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 0.15})
figsize = (fig_side, fig_side)
fig = plt.figure(figsize=figsize)
ax = plt.axes()

if show_title:
    fig_title = category_select
else:
    fig_title = " "
plt.title(fig_title, fontsize=35)

# captions on graph (most common)
texts = []
if show_captions:
    for i in range(0,number_of_labels):
        dat0 = data_shade_center[data_shade_center[column_identifier] == label_text[i]]
        labx = dat0['xcoor'].values[0]
        laby = dat0['ycoor'].values[0]
        texts.append(plt.text(labx, laby, label_text[i], alpha=cat_txt_transp, \
            size=12, weight = 'normal', style='italic', color=cat_txt_col))      

    if adjust_labels:
        adjust_text(texts)

# KDE density plots (with or without contour lines)
if contour_on:
    sns.kdeplot(data=data_to_show, x ='xcoor', y='ycoor', color = shade_color, \
        alpha = 1, n_levels=number_of_levels, legend=False)
if shade_on:
    sns.kdeplot(data=data_to_show, x ='xcoor', y='ycoor', shade=True, color = shade_color, \
        alpha = shade_alpha, n_levels=number_of_levels, thresh=low_thresh, legend=False)

# individual points
if use_overlay == 1:
    plt.scatter(data_to_show['xcoor'], data_to_show['ycoor'], alpha=marker_transparence, \
        s=marker_size , label=None, c=marker_color)

# background graph stuff
plt.xlabel('x')
plt.ylabel('y')
plt.axis('equal')

myLineWidth = 0.35
circle1 = plt.Circle((0.5, 0.5), .125, linewidth = myLineWidth, color='blue', fill=False)
circle2 = plt.Circle((0.5, 0.5), .25, linewidth = myLineWidth, color='blue', fill=False)
circle3 = plt.Circle((0.5, 0.5), .375, linewidth = myLineWidth, color='blue', fill=False)

fig = plt.gcf()
ax = fig.gca()
ax.grid(False)
ax.add_artist(circle1)
ax.add_artist(circle2)
ax.add_artist(circle3)

ax.plot([0.5,0.5], [0,1.00], 'b-', linewidth = myLineWidth)
ax.plot([0,1.00], [0.5,0.5], 'b-', linewidth = myLineWidth)
ax.plot([0,1.00], [1.00,0], 'b-', linewidth = myLineWidth)               
ax.plot([0,1.00], [0,1.00], 'b-', linewidth = myLineWidth)                 
plt.xlim(crop_xmin, crop_xmax)
plt.ylim(crop_ymin, crop_ymax)

st.write(fig)

if st.checkbox('Show records in chosen category', value=False, key='show_df_category'):
    st.dataframe(data_to_show)

with st.expander("Export map ..."):
    destination = st.text_input("Export to:", value=my_workspace, key="export_destination")
    exportFile = st.text_input("Export map file:", value=export_file_suggested_name, \
        key="export_file_name")
    img_res = st.number_input('Image resolution in dpi', min_value=125, max_value=500, \
        value=300, key='img_resolution')
    export_map = st.button('Export')
    if export_map:
        fig.savefig(destination + exportFile, bbox_inches = 'tight', dpi = img_res)

# with st.expander("Common keywords ..."):
#     # show most common keywords for selected set of records
#     selResKey = data_keywords[data_keywords[column_identifier] == category_select]
#     selResKey = selResKey.dropna()
#     selResKey.sort_values(by='year', ascending=0)

#     totList = selResKey['keyword'].value_counts()
#     totList = pd.DataFrame(totList).reset_index()

#     totChart = alt.Chart(totList[ : 60]).mark_bar(color='lightblue').encode(
#         x='keyword:Q',
#         y=alt.Y('index:N', sort=alt.EncodingSortField(field="keyword", op="sum", order='descending'))
#     ).properties(title="All years", width=750)

#     st.altair_chart(totChart)

print('... mapping')