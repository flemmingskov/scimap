'''
File: map1_distribution.py
Author: Flemming Skov 
Purpose: Maps the density of papers for individual subject categories, keywords, researchers
and institutions . 
Latest version: May 24, 2022
'''

st.header("KEYWORD BROWSER")
st.markdown('___')

#st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information
# my_workspace = (primary_path + secondary_path)

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
        This tools can be used to browse and visualize keywords using filters (bearing, distance, weight))

    """)

    for t in range(expander_space):
        st.write(' ')

# WORKSPACE & FILE EXPANDER
with st.expander("Workspace and data bases ..."):
    secondary_path = st.selectbox("Path to primary workspace: ", list_secondary_paths)
    my_workspace = (primary_path + secondary_path)

    ws_config_file = my_workspace + 'config.txt'
    exec(open(ws_config_file).read())

    # open connection to keyword database
    coordinates_data_path = my_workspace + st.text_input('coordinate data base \
        (reference system): ', default_coordinates_db)
    st.success("db found: " + coordinates_data_path) if os.path.isfile(coordinates_data_path) \
        else st.info("db does not exist")

    for t in range(expander_space):
        st.write(' ')


#read coordinates for keywords and save a copy in the new map.db
coordinates_db_connection = sqlite3.connect(coordinates_data_path)
coordinates_data = pd.read_sql_query('select * from keyword_coordinates;', coordinates_db_connection)

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

    number_of_labels = col1.slider('Number of text labels (from them most common):', 0, 150, 15, 1, \
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

# # FILTER EXPANDER
with st.expander("Filters ..."):

    values_bearing = st.slider('Bearing - select range', 0, 360, (0, 180))
    bearing_top = values_bearing[1]
    bearing_bottom = values_bearing[0]

    values_distance = st.slider('Distance - select range', 0.0, 0.99, (0.0, 0.55))
    distance_top = values_distance[1]
    distance_bottom = values_distance[0]

    values_degree = st.slider('Degree - select range', 0, 3000, (0, 3000))
    degree_top = distance_top = values_degree[1]
    degree_bottom = values_degree[0]
    

    coordinates_data = coordinates_data[((coordinates_data['bearing']>= bearing_bottom) & \
             (coordinates_data['bearing']<= bearing_top))]

    coordinates_data = coordinates_data[((coordinates_data['distance']>= distance_bottom) & \
             (coordinates_data['distance']<= distance_top))]

    coordinates_data = coordinates_data[((coordinates_data['degree']>= degree_bottom) & \
             (coordinates_data['degree']<= degree_top))]

    st.dataframe(coordinates_data)



##  MAIN ACTION
st.markdown(' ')
st.subheader('MAPS & DATA')

# layout and outline
sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 0.15})
figsize = (fig_side, fig_side)
fig = plt.figure(figsize=figsize)
ax = plt.axes()

# if show_title:
#     fig_title = category_select
# else:
#     fig_title = " "
# plt.title(fig_title, fontsize=35)

# captions on graph (most common)
# texts = []
# if show_captions:
#     for i in range(0,number_of_labels):
#         labx = coordinates_data['xcoor'].values[i]
#         laby = labx = coordinates_data['xcoor'].values[i]
#         label_text = coordinates_data['keyword'].values[i]
#         texts.append(plt.text(labx, laby, label_text, alpha=cat_txt_transp, \
#             size=12, weight = 'normal', style='italic', color=cat_txt_col))      

#     if adjust_labels:
#         adjust_text(texts)

if show_captions:
    for i, row in coordinates_data.iterrows():
        ax.annotate(row[1], (row[2], row[3]))

# KDE density plots (with or without contour lines)
if contour_on:
    sns.kdeplot(data=coordinates_data, x ='xcoor', y='ycoor', color = shade_color, \
        alpha = 1, n_levels=number_of_levels, legend=False)
if shade_on:
    sns.kdeplot(data=coordinates_data, x ='xcoor', y='ycoor', shade=True, color = shade_color, \
        alpha = shade_alpha, n_levels=number_of_levels, thresh=low_thresh, legend=False)

# individual points
if use_overlay == 1:
    plt.scatter(coordinates_data['xcoor'], coordinates_data['ycoor'], alpha=marker_transparence, \
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

# if st.checkbox('Show records in chosen category', value=False, key='show_df_category'):
#     st.dataframe(data_to_show)

# with st.expander("Export map ..."):
#     destination = st.text_input("Export to:", value=my_workspace, key="export_destination")
#     exportFile = st.text_input("Export map file:", value=export_file_suggested_name, \
#         key="export_file_name")
#     img_res = st.number_input('Image resolution in dpi', min_value=125, max_value=500, \
#         value=300, key='img_resolution')
#     export_map = st.button('Export')
#     if export_map:
#         fig.savefig(destination + exportFile, bbox_inches = 'tight', dpi = img_res)

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