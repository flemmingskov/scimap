'''
File: tool6_adjust_layout.py
Author: Flemming Skov 
Purpose: This script makes it possible to adjust the graph
Latest version: May 22 2021
'''

st.header("ADJUST GRAPH LAYOUT")
st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information

# ABOUT EXPANDER
with st.expander("About ..."):
    st.subheader('Help:')
    st.markdown(
        f"""       
        In some cases keywords tend to clump around the center of the graph
        and in other cases they are spread unvevenly in the landscape.
        The settings here may be used to adjust the layout and produced a more useful map.
        This is done using a simple normalization. Set the donut hole size to push the innter points outwards
        and normalize to new values. The x- and y-adjust values simply move the center of the graph.  
    """)

    add_empty_lines(expander_space)

# WORKSPACE & FILE EXPANDER
with st.expander("Workspace and data bases ..."):
    secondary_path = st.selectbox("Path to primary workspace: ", list_secondary_paths)
    my_workspace = (primary_path + secondary_path)

    ws_config_file = my_workspace + 'config.txt'
    exec(open(ws_config_file).read())

    # open connection to map database
    coordinates_db = my_workspace + st.text_input('data base: ', default_coordinates_db)
    st.success("db found: " + coordinates_db) if os.path.isfile(coordinates_db) else st.info("db does not exist")

    add_empty_lines(expander_space)

# Setting basic variables
conn = sqlite3.connect(coordinates_db) 
keyword_FR = pd.read_sql_query('select * from keyword_raw_coordinates;', conn)

sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 0.15})

# SHOW GRAPH AND DATA EXPANDER
st.markdown(' ')
st.subheader('DEFAULT LAYOUT')
st.write(' ')

with st.expander("Show basic layout and data ..."):
    # FRUCHTERMAN-REINGOLD UNPROCESSED
    run_FR_map =  st.checkbox('Show original Fruchterman-Reingold layout', value=False,  key='runFR')

    if run_FR_map:
        fig = plt.figure(figsize=(15,15))
        ax = plt.axes()
        
        wdegree_level = st.slider('Weighted degree (show only keywords with a value above in the original diagram):', min_value=0, max_value=2500, value=0, step=100, key='wdegreelevel')
        keyword_FR_sel = keyword_FR[keyword_FR['wdegree']>= wdegree_level]

        sns.kdeplot(data = keyword_FR_sel, x = 'xcoor', y = 'ycoor', alpha = 0.55, fill=True, legend=False, thresh=0.01)
        sns.kdeplot(data = keyword_FR_sel, x = 'xcoor', y = 'ycoor', n_levels=10, cmap=plt.cm.winter)
        plt.scatter(keyword_FR_sel['xcoor'], keyword_FR_sel['ycoor'], alpha=0.4, s=3, label=None, c='blue')
        plt.xlabel('x')
        plt.ylabel('y')  
        linWid = 0.35
        
        circle1 = plt.Circle((0.5, 0.5), .125, linewidth = linWid, color='gray', fill=False)
        circle2 = plt.Circle((0.5, 0.5), .25, linewidth = linWid, color='gray', fill=False)
        circle3 = plt.Circle((0.5, 0.5), .375, linewidth = linWid, color='gray', fill=False)        
        ax.add_artist(circle1)
        ax.add_artist(circle2)
        ax.add_artist(circle3)                  
        ax.plot([0.5,0.5], [0,1.00], 'b-', linewidth = linWid)
        ax.plot([0,1.00], [0.5,0.5], 'b-', linewidth = linWid)
        ax.plot([0,1.00], [1.00,0], 'b-', linewidth = linWid)               
        ax.plot([0,1.00], [0,1.00], 'b-', linewidth = linWid)            
        ax.plot([0,0], [0,1.0], 'b-', linewidth = linWid)
        ax.plot([1.0,1.0], [0,1.0], 'b-', linewidth = linWid)
        ax.plot([0,1.0], [1,1.0], 'b-', linewidth = linWid)
        ax.plot([0,1.0], [0,0], 'b-', linewidth = linWid)   
        ax.grid(False)
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)

        st.write(fig)
        st.dataframe(keyword_FR_sel)

##  MAIN ACTION
st.markdown(' ')
st.subheader('ADJUST GRAPH LAYOUT')
st.write(' ')

# SETTINGS EXPANDER
with st.expander("Adjustment settings  ..."):
    donut_hole = st.slider('Donut hole in the middle:', \
         0.0, 0.5, 0.05, 0.05, key='donut_hole')

    x_adjust = st.slider('Adjust x-value:', -0.2, 0.2, 0.0, 0.01, key='adjustX')
    y_adjust = st.slider('Adjust y-value:', -0.2, 0.2, 0.0, 0.01, key='adjustY')

    run_save_coord =  st.checkbox('Save adjusted coordinates while running', value=False, key='save_new_coordinates')

    add_empty_lines(expander_space)

# EXPANDED DATA
run_FR_adjust =  st.checkbox('Show adjusted layout', value=False,  key='runFRexp')

if run_FR_adjust:
    begin_time = datetime.datetime.now()

    try:
        with st.spinner('Calculating  ...'):
            x_list = []
            y_list = []
            distance_list = []
            bearing_list = []
            xnew_list = []
            ynew_list = []
            newdistance_list = []
            keyword_list = []
          
            max_distance = keyword_FR["distance"].max()

            for row in keyword_FR.itertuples(index=False):
                keyword_list.append(row[1])
                x_list.append(row[2])
                y_list.append(row[3])
                distance_list.append(row[11])
                bearing_list.append(row[12])

                new_dist = normalize([row[11]], {'actual': {'lower': 0, 'upper': max_distance}, 'desired': {'lower': donut_hole, 'upper': 0.5,}})
                new_dist = float(new_dist[0])
                newdistance_list.append(new_dist)

                new_x = new_dist*np.cos(np.radians(90-row[12]))
                new_y = new_dist*np.sin(np.radians(90-row[12]))

                # vertical and horizontal adjustments
                new_x = new_x + x_adjust
                new_y = new_y + y_adjust  

                if row[2] >= 0.5:
                    new_x = 0.5 + new_x
                else:
                    new_x = 0.5 + new_x
                if row[3] >= 0.5:
                    new_y = 0.5 + new_y
                else:
                    new_y = 0.5 + new_y

                # set limits between 0 and 1
                if new_x < 0:
                    new_x = 0
                elif new_x > 1:
                    new_x = 1
                if new_y < 0:
                    new_y = 0
                elif new_y > 1:
                    new_y = 1 

        
                xnew_list.append(new_x)            
                ynew_list.append(new_y)
                
            data_temp = pd.DataFrame({'keyword': keyword_list, 'x_old': x_list,
                                    'y_old': y_list, 'bearing': bearing_list, 'distance_old': distance_list,
                                    'distance_new': newdistance_list, 'xcoor': xnew_list, 'ycoor': ynew_list})


            # create plot
            fig = plt.figure(figsize=(15,15))
            ax = plt.axes()
            
            sns.kdeplot(data=data_temp, x = 'xcoor', y = 'ycoor', alpha = 0.55, fill=True, legend=False, thresh=0.01)
            sns.kdeplot(data= data_temp, x = 'xcoor', y = 'ycoor', n_levels=10, cmap=plt.cm.winter)
            plt.scatter(data_temp['xcoor'], data_temp['ycoor'], alpha=0.4, s=3, label=None, c='blue')
            plt.xlabel('x')
            plt.ylabel('y')  
            linWid = 0.35
            
            circle1 = plt.Circle((0.5, 0.5), .125, linewidth = linWid, color='gray', fill=False)
            circle2 = plt.Circle((0.5, 0.5), .25, linewidth = linWid, color='gray', fill=False)
            circle3 = plt.Circle((0.5, 0.5), .375, linewidth = linWid, color='gray', fill=False)        
            ax.add_artist(circle1)
            ax.add_artist(circle2)
            ax.add_artist(circle3)                  
            ax.plot([0.5,0.5], [0,1.00], 'b-', linewidth = linWid)
            ax.plot([0,1.00], [0.5,0.5], 'b-', linewidth = linWid)
            ax.plot([0,1.00], [1.00,0], 'b-', linewidth = linWid)               
            ax.plot([0,1.00], [0,1.00], 'b-', linewidth = linWid)            
            ax.plot([0,0], [0,1.0], 'b-', linewidth = linWid)
            ax.plot([1.0,1.0], [0,1.0], 'b-', linewidth = linWid)
            ax.plot([0,1.0], [1,1.0], 'b-', linewidth = linWid)
            ax.plot([0,1.0], [0,0], 'b-', linewidth = linWid)   
            ax.grid(False)
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            
            st.write(fig)

        if run_save_coord:
            keyword_FR = keyword_FR.drop(columns=['index', 'xcoor', 'ycoor'])
            keyword_FR.insert(1, "xcoor", xnew_list, True)
            keyword_FR.insert(2, "ycoor", ynew_list, True)
            
            keyword_FR = keyword_FR.reset_index(drop=True)   
            keyword_FR.to_sql('keyword_coordinates', conn, if_exists='replace')
            st.success("Adjusted keyword coordinates saved")

    except Exception as e:
        print("Program Error: ")
        print(e)

    finally:
        print('... step 6 - graph layout adjusted in: ' + str(datetime.datetime.now() - begin_time))   


# NOTES AND COMMENTARIES #####################################################
'''

FURTHER IMPROVEMENT, NOT YET IMPLEMENTED: ROTATING PLOT
import math

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy
'''