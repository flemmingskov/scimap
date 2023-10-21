'''
File: tool7_map_db.py
Author: Flemming Skov 
Purpose: This script produced a map database where keyword coordinates from the reference map
        may be added to any data file   
Latest version: May 22 2021
'''

st.header("PREPARE DATA FOR MAPPING")
st.markdown('___')
st.subheader('CONTROLS & SETTINGS')

exec(open("config.py").read())  # file with stored basic information

# ABOUT EXPANDER
with st.expander("About ..."):
    st.subheader('Help:')
    st.markdown(
        f"""       
        This process prepares the map database used to store information related
        to papers, persons, categories and keywords (center and spread), This database is
        again used as input to the mapping tools  
    """)

    add_empty_lines(expander_space)

# WORKSPACE & FILE EXPANDER
with st.expander("Workspace and data bases ..."):
    secondary_path = st.selectbox("Path to primary workspace: ", list_secondary_paths)
    my_workspace = (primary_path + secondary_path)

    ws_config_file = my_workspace + 'config.txt'
    exec(open(ws_config_file).read())

    # open connection to map database
    overlay_data_path = my_workspace + st.text_input('data base (to be overlayed reference \
        system): ', default_data_db)
    st.success("db found: " + overlay_data_path) if os.path.isfile(overlay_data_path) \
        else st.info("overlay database does not exist")

    # open connection to map database
    coordinates_data_path = my_workspace + st.text_input('coordinate data base \
        (reference system): ', default_coordinates_db)
    st.success("db found: " + coordinates_data_path) if os.path.isfile(coordinates_data_path) \
        else st.info("db does not exist")

    # open connection to map database
    output_data_path = my_workspace + st.text_input('map db: ', default_map_db)
    st.success("db found: " + output_data_path) if os.path.isfile(output_data_path) \
        else st.info("db does not exist")

    add_empty_lines(expander_space)

# SETTINGS EXPANDER
with st.expander("Settings and controls ..."):   
    st.write('Include keywords from:')
    run_keywords = st.checkbox('Web of Science', value=True, key='runKeywords')
    run_title = st.checkbox('Title', value=False, key='runTitle')
    run_abstract = st.checkbox('Abstract', value=False, key='runKAbstract')

    calculation_mode = st.radio(
     "Calculate position of papers using:",
     ('mean', 'median'))

    add_empty_lines(expander_space)

##  MAIN ACTION
st.markdown(' ')
st.subheader('PREPARE MAPPING FILE')
st.write(' ')
run_script =  st.button('Run script')

if run_script:
    synonyms = import_synonyms()
    begin_time = datetime.datetime.now()

    try:
        with st.spinner('Calculating ...'):  
     
            overlay_db_connection = sqlite3.connect(overlay_data_path)
            coordinates_db_connection = sqlite3.connect(coordinates_data_path)
            outputdata_db_connection = sqlite3.connect(output_data_path)
        
            overlay_keywords = pd.read_sql_query('select * from keyword_collection;', overlay_db_connection).fillna('')    
            overlay_data = pd.read_sql_query('select * from wosdata;', overlay_db_connection).fillna('')
            overlay_links = pd.read_sql_query('select * from links;', overlay_db_connection)

            #read coordinates for keywords and save a copy in the new map.db
            coordinates_data = pd.read_sql_query('select * from keyword_coordinates;', coordinates_db_connection)
            coordinates_data.to_sql('keyC', outputdata_db_connection, if_exists='replace')

            search_string = '(overlay_links.cites >= 0)'
            subset = overlay_links.loc[eval(search_string), ['wosid', 'label']]
            dataframe_in = pd.merge(subset, overlay_data, on='wosid', how='inner')
            dataframe_in = dataframe_in.drop_duplicates(['wosid'])
            dataframe_in = dataframe_in.dropna()
            dataframe_in = dataframe_in[['authors', 'title', 'kw1', 'kw2', 'abstr', 'inst',
                            'email', 'autID', 'funding', 'cites', 'journal', 'year',
                            'wos_sub_cat1', 'wos_sub_cat2', 'wosid', 'time_stamp']]

            WoS_category = overlay_links.loc[eval(search_string), ['wosid', 'category']]
            del overlay_data           

        # STEP 1 - linking individual keywords to papers

            wos_list = []
            year_list = []
            kw_list = []

            for row in overlay_keywords.itertuples(index=False):
                wos_id = row[1]
                yr = row[6]

                # regular keywords
                if run_keywords:
                    ## user keywords
                    keyword_list = row[2]
                    for kw in keyword_list.split(";"):
                        if kw != "":
                            wos_list.append(wos_id)
                            kw_list.append(kw)
                            year_list.append(yr)
                            
                    ## keywords plus WoS
                    keyword_list = row[3]
                    for kw in keyword_list.split(";"):
                        if kw != "":
                            wos_list.append(wos_id)
                            kw_list.append(kw)
                            year_list.append(yr)

                # keywords from title
                if run_title:
                    keyword_list = row[4]
                    for kw in keyword_list.split(";"):
                        if kw != "":
                            wos_list.append(wos_id)
                            kw_list.append(kw)
                            year_list.append(yr)
            
                # keywords from abstract
                if run_abstract:
                    keyword_list = row[5]
                    for kw in keyword_list.split(";"):
                        if kw != "":
                            wos_list.append(wos_id)
                            kw_list.append(kw)
                            year_list.append(yr)

            keywords_df = pd.DataFrame({'keyword': kw_list, 'year': year_list, 'wosid': wos_list})    

        # STEP 2 - linking individual institutions and countries to papers
            # wosList = []
            # citesList = []
            # instList = []
            # countryList = []
            # collList = []
            
            wosList, citesList, instList, countryList, collList = ([] for _ in range(5))
            
            sqRegex = re.compile(r'\[.*?\]\s')
            usRegex = re.compile(r'(\D\D)\s(\d\d\d\d\d)\s(usa)')           
        
            # for index, row in dataframe_in.iterrows():
            for row in dataframe_in.itertuples(index=False):

                wosid = row[14]
                cites = row[9]
                adresses = row[5]
                adresses = sqRegex.sub("", adresses)

                instColl = []
                for institution in adresses.split(";"):

                    if institution != "":
                        instParts = institution.split(',')
                        mainInst = instParts[0]
                        mainInst = mainInst.lower()
                        mainInst = mainInst.strip()
                        if (synonyms.get(mainInst, "none")) != 'none':
                            mainInst = synonyms.get(mainInst)
                        mainInst = mainInst.replace(" ", "-")
            
                        country = instParts[-1]
                        country = country.lower()
                        country = country.strip()
                        usmatch = re.search(usRegex, country)
                        if usmatch:
                            country = usmatch.group(3) + " " + usmatch.group(1)
                        if (synonyms.get(country, "none")) != 'none':
                            country = synonyms.get(country)
                        country = country.replace(" ", "-")
                            
                        fullInst = country + "_" + mainInst    

                        if fullInst not in instColl:
                            instColl.append(fullInst)
                        
                        wosList.append(wosid)
                        citesList.append(cites) 
                        instList.append(fullInst)
                        countryList.append(country)

                collList.append(instColl)

            dfStep2 = pd.DataFrame({'institution': instList, 'country': countryList, 'cites': citesList, 'wosid': wosList})
            dfStep2 = dfStep2[2:]
            dfStep2 = dfStep2[['wosid', 'country', 'cites', 'institution']]

            dfStep2.to_sql('papGeo', outputdata_db_connection, if_exists='replace')


        # STEP 3 - pivot to find median x- and y-coords per WoS record
            mergeWoSCoord = keywords_df.merge(coordinates_data, on='keyword', how='left')

            WoS_pivot_coord = pd.pivot_table(mergeWoSCoord, index=['wosid'],
                                        values=['xcoor', 'ycoor', 'year'],
                                        aggfunc=calculation_mode)  #np.sum
                         

            WoS_pivot_coord = WoS_pivot_coord[['xcoor', 'ycoor', 'year']].iloc[1:]
            WoS_pivot_coord.reset_index(inplace=True)

            wosCoor = WoS_pivot_coord.merge(subset, on='wosid', how='left')
            wosCoor = wosCoor.drop_duplicates(['wosid'])
            
            #  CHANGE APRIL 15 2023 (original):  dataInCites = dataframe_in[['wosid', 'cites', 'authors', 'title', ]]
            dataInCites = dataframe_in[['wosid', 'cites', 'authors', 'title', 'journal' ]]
        
            dataInCites = dataInCites.sort_values(['cites'], ascending=[0])
            dataInCites.insert(0, 'rank', range(1, len(dataInCites)+1))
        
            wosCoor = wosCoor.merge(dataInCites, on='wosid', how='left')
            wosCoor = wosCoor.dropna()
            wosCoor.to_sql('papI', outputdata_db_connection, if_exists='replace')
            wosCoorC = wosCoor[['wosid', 'xcoor', 'ycoor', 'year']]
            wosCoorC.to_sql('papC', outputdata_db_connection, if_exists='replace')


            # calculating the distribution of keywords in individual papers
            df_keywords_with_coor = keywords_df.merge(wosCoorC, on='wosid', how='left')
            df_keywords_with_coor = df_keywords_with_coor.dropna()
            df_keywords_with_coor = df_keywords_with_coor[['keyword', 'xcoor', 'ycoor', 'wosid', 'year_x']]
            df_keywords_with_coor.columns = ['keyword', 'xcoor', 'ycoor', 'wosid', 'year']

            df_keywords_with_coor.to_sql('papK', outputdata_db_connection, if_exists='replace')
            
        # STEP 4 - calculating coordinates for WoS subject categories
            mergeCatCoord = pd.merge(WoS_category, WoS_pivot_coord, on='wosid', how='left')          
            mergeCatCoord = mergeCatCoord[['wosid', 'category', 'xcoor', 'ycoor',
                    'year']]
            
            WoS_pivot_category = pd.pivot_table(mergeCatCoord, index=['category'],
                            values=['xcoor', 'ycoor'],
                            aggfunc=calculation_mode)
            WoS_pivot_category.reset_index(inplace=True)
            
            # Counting unique occurrences of subject categories
            catCount = pd.DataFrame(WoS_category['category'].value_counts())  
            catCount['label'] = catCount.index
            catCount.index = range(len(catCount))
            catCount.columns = ["numOcc", "category"]
            catCount = catCount[["category", "numOcc"]]
            
            # Centroids for each WoS category
            WoS_pivot_category = WoS_pivot_category.merge(catCount, on='category', how='left')
            WoS_pivot_category = WoS_pivot_category.dropna()
            WoS_pivot_category = WoS_pivot_category.sort_values('numOcc', ascending=False)
            #WoS_pivot_category = WoS_pivot_category.drop('year', axis=1)
            wosCatPivotW = WoS_pivot_category
            wosCatPivotW.columns = ['category', 'xcoor','ycoor', 'weight']
            wosCatPivotW.to_sql('catC', outputdata_db_connection, if_exists='replace')
            
            # WoS-id, category, x- and y-coordinates + numOcc (for Bokeh graph)
            mergeCatCoord = mergeCatCoord.merge(catCount, on='category', how='left')
            mergeCatCoord = mergeCatCoord.dropna()
            mergeCatCoord = mergeCatCoord[mergeCatCoord['numOcc'] > 5]
            
            mergeCatCoord = mergeCatCoord.merge(wosCoor, on='wosid', how='left')
            mergeCatCoord = mergeCatCoord[['wosid','category','xcoor_x','ycoor_x',
                    'year_y','numOcc']]
            mergeCatCoord.columns = ['wosid','category','xcoor','ycoor', 'year', 'weight']        
            mergeCatCoord.to_sql('catD', outputdata_db_connection, if_exists='replace')
            
            # And then for catK  -  all combinations of keyords and category
            catKmerge = pd.merge(keywords_df, mergeCatCoord)          
            catKmerge.to_sql('catK', outputdata_db_connection, if_exists='replace')    
        
        # STEP 5 - finding mean coordinates and sum cites for countries      
            instMerge = pd.merge(dfStep2, WoS_pivot_coord, on='wosid', how='left')
            
            ##  mean coordinates
            country_pivot_coor = pd.pivot_table(instMerge, index=['country'],
                                        values=['xcoor', 'ycoor'],
                                        aggfunc=calculation_mode)
            country_pivot_coor = country_pivot_coor[['xcoor', 'ycoor']].iloc[1:]
            country_pivot_coor.reset_index(inplace=True)

            ##  sum cites
            country_pivot_cites = pd.pivot_table(instMerge, index=['country'],
                                        values=['cites'],
                                        aggfunc='sum')
            country_pivot_cites = country_pivot_cites[['cites']].iloc[1:]
            country_pivot_cites.reset_index(inplace=True)
            

            ## number of authorships per institute
            counttry_pivot_count = pd.DataFrame(dfStep2['country'].value_counts())
            
            counttry_pivot_count['label'] = counttry_pivot_count.index
            counttry_pivot_count.index = range(len(counttry_pivot_count))
            counttry_pivot_count.columns = ["numOcc", "country"]
            counttry_pivot_count = counttry_pivot_count[["country", "numOcc"]]
            
            ##  merging tables
            country_pivot_coor = country_pivot_coor.merge(country_pivot_cites, on='country', how='left')
            country_pivot_coor = country_pivot_coor.merge(counttry_pivot_count, on='country', how='left')
            country_pivot_coor.columns = ['country', 'xcoor','ycoor', 'cites', 'weight']
            country_pivot_coor.to_sql('couC', outputdata_db_connection, if_exists='replace')
            
        # STEP 6 - putting coordinates on institutions
            ##  mean coordinates

            institution_pivot_coor = pd.pivot_table(instMerge, index=['institution'],
                                        values=['xcoor', 'ycoor'],
                                        aggfunc=calculation_mode)
            institution_pivot_coor = institution_pivot_coor[['xcoor', 'ycoor']].iloc[1:]
            institution_pivot_coor.reset_index(inplace=True)

            ##  sum cites
            institution_pivot_cites = pd.pivot_table(instMerge, index=['institution'],
                                        values=['cites'],
                                        aggfunc='sum')
            institution_pivot_cites = institution_pivot_cites[['cites']].iloc[1:]
            institution_pivot_cites.reset_index(inplace=True)

            ## number of authorships per institute
            institution_pivot_count = pd.DataFrame(dfStep2['institution'].value_counts())
            institution_pivot_count['label'] = institution_pivot_count.index
            institution_pivot_count.index = range(len(institution_pivot_count))
            institution_pivot_count.columns = ["numOcc", "institution"]
            institution_pivot_count = institution_pivot_count[["institution", "numOcc"]]

            ##  merging tables
            institution_pivot_coor = institution_pivot_coor.merge(institution_pivot_cites, on='institution', how='left')
            institution_pivot_coor = institution_pivot_coor.merge(institution_pivot_count, on='institution', how='left')
            institution_pivot_coor['ID'] = institution_pivot_coor.index
            institution_pivot_coor = institution_pivot_coor[['ID', 'institution', 'xcoor', 'ycoor', 'cites', 'numOcc']]
            institution_pivot_coor.columns = ['ID', 'inst', 'xcoor', 'ycoor', 'cites', 'weight'] 

            ## save to excel file (NB: Dec17 also write instMerge to file)
            institution_pivot_coor.to_sql('insC', outputdata_db_connection, if_exists='replace')
            
            instMerge.columns = ['wosid', 'country', 'cites', 'inst', 'xcoor', 'ycoor', 'year']
            instMerge.to_sql('insD', outputdata_db_connection, if_exists='replace')

            print('... step 7 - preparation of map, first steps in: ' + str(datetime.datetime.now() - begin_time))

        # STEP 7 - putting coordinates on people
            author_WoS = dataframe_in
            author_WoS.replace(r'\s+', np.nan, regex=True).replace('', np.nan)
            author_WoS = author_WoS.fillna('')

            wosList = []
            autList = []
            yearList = []
            kw1List = []
            kw2List = []

            #for index, row in dataframe_in.iterrows():
            for row in dataframe_in.itertuples(index=False):
                au = row[0]
                wosid = row[14]
                yr = row[11]
                kw1 = row[2]
                kw2 = row[3]
                cat1list = row[12]
                cat2list = row[13]

                for individual in au.split(";"):
                    for kw in kw1.split(";"):
                        if kw != "":
                            coll_kw = ""
                            kw = kw.replace("-", " ")
                            for kwpart in kw.split(" "):
                                if kwpart != "":
                                    kwpart = kwpart.lower()
                                    kwpart = wnl.lemmatize(kwpart)
                                    if (synonyms.get(kwpart, "none")) != 'none':
                                        kwpart = synonyms.get(kwpart)

                                    if coll_kw != "":
                                        coll_kw = coll_kw + "-" + kwpart
                                    if coll_kw == "":
                                        coll_kw = coll_kw + kwpart
                                    if (synonyms.get(coll_kw, "none")) != 'none':
                                        coll_kw = synonyms.get(coll_kw)

                            individual = individual.lower().strip().replace(", ", ".")
                            
                            #if (synonyms.get(individual, "none")) != 'none':
                            if individual in synonyms:
                                individual = synonyms.get(individual)

                            wosList.append(wosid)
                            yearList.append(yr)
                            autList.append(individual)
                            kw2List.append(coll_kw)

                    for kw in kw2.split(";"):
                        if kw != "":
                            coll_kw = ""
                            kw = kw.replace("-", " ")
                            for kwpart in kw.split(" "):
                                if kwpart != "":
                                    kwpart = kwpart.lower()
                                    kwpart = wnl.lemmatize(kwpart)
                                    if (synonyms.get(kwpart, "none")) != 'none':
                                        kwpart = synonyms.get(kwpart)

                                    if coll_kw != "":
                                        coll_kw = coll_kw + "-" + kwpart
                                    if coll_kw == "":
                                        coll_kw = coll_kw + kwpart
                                    if (synonyms.get(coll_kw, "none")) != 'none':
                                        coll_kw = synonyms.get(coll_kw)
                                        
                            individual = individual.lower().strip().replace(", ", ".")
                            
                            if (synonyms.get(individual, "none")) != 'none':
                                individual = synonyms.get(individual)

                            wosList.append(wosid)
                            yearList.append(yr)
                            autList.append(individual)
                            kw2List.append(coll_kw)

            author_WoS = pd.DataFrame({'author': autList, 'wosid': wosList,
                                    'year': yearList, 'keyword': kw2List})
            author_WoS = author_WoS[2:]
            author_WoS = author_WoS[['author', 'year', 'keyword', 'wosid']]
            author_WoS = author_WoS.fillna('')
            author_merge = pd.merge(author_WoS, WoS_pivot_coord, on='wosid', how='left')
            
        #   prepare data for the autD db where author-wosid are linked    
            autMergeD = author_merge[["author", "xcoor", "ycoor", "wosid", "year_y"]]
            autMergeDNoDup = autMergeD.drop_duplicates(['author', 'wosid'])
            autMergeDNoDup.columns = ['name', 'xcoor', 'ycoor', 'wosid', 'year']
            autMergeDNoDup.to_sql('autD', outputdata_db_connection, if_exists='replace')
            
        #   prepare data for the autK db where all author-keyword relations are shown
            autMergeK = author_merge[["author", "xcoor", "ycoor", "wosid", "keyword","year_y"]]
            autMergeK.columns = ['name', 'xcoor', 'ycoor', 'wosid', 'keyword', 'year']
            autMergeK.to_sql('autK', outputdata_db_connection, if_exists='replace')
            
            author_pivot_coord = pd.pivot_table(author_merge, index=['author'],
                    values=['xcoor', 'ycoor'],
                    aggfunc=calculation_mode)

            author_pivot_coord.reset_index(inplace=True)
            author_pivot_coord = author_pivot_coord.dropna()
            
            # Counting unique occurrences and adding IDs
            number_of_authors = pd.DataFrame(author_WoS['author'].value_counts())
            number_of_authors['label'] = number_of_authors.index
            number_of_authors.index = range(len(number_of_authors))
            number_of_authors.columns = ["numOcc", "author"]
            number_of_authors = number_of_authors[["author", "numOcc"]]
            author_pivot_coord = author_pivot_coord.merge(number_of_authors, on='author', how='left')
            author_pivot_coord = author_pivot_coord.sort_values('numOcc', ascending=False)
            author_pivot_coord['ID'] = author_pivot_coord.index
            author_pivot_coord = author_pivot_coord[['ID', 'author', 'xcoor', 'ycoor', 'numOcc']]
            author_pivot_coord.columns = ['ID', 'name', 'xcoor', 'ycoor', 'weight'] 
            author_pivot_coord.to_sql('autC', outputdata_db_connection, if_exists='replace')

        # STEP 8 - finding mean coordinates and sum cites for individual Journals      

            ##  mean coordinates
            journal_pivot_coor = pd.pivot_table(wosCoor, index=['journal'],
                                        values=['xcoor', 'ycoor'],
                                        aggfunc=calculation_mode)
            journal_pivot_coor = journal_pivot_coor[['xcoor', 'ycoor']].iloc[1:]
            journal_pivot_coor.reset_index(inplace=True)

           ##  sum cites
            journal_pivot_cites = pd.pivot_table(wosCoor, index=['journal'],
                                        values=['cites'],
                                        aggfunc='sum')
            journal_pivot_cites = journal_pivot_cites[['cites']].iloc[1:]
            journal_pivot_cites.reset_index(inplace=True)
           
            ##  merging tables
            journal_pivot_coor = journal_pivot_coor.merge(journal_pivot_cites, on='journal', how='left')
            #journal_pivot_coor = journal_pivot_coor.merge(counttry_pivot_count, on='country', how='left')
            journal_pivot_coor.columns = ['journal', 'xcoor','ycoor', 'cites']
            journal_pivot_coor.to_sql('jourC', outputdata_db_connection, if_exists='replace') 
            
        # STEP 9 - closing connection
            outputdata_db_connection.close()
            print('... step 7 - preparation of map, including last step in: ' + str(datetime.datetime.now() - begin_time))     

    except Exception as e:
        print("Program Error: ")
        print(e)

    finally:
        st.success("Data for overlay mapping prepared")