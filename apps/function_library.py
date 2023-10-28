# FUNCTION LIBRARY
# This file contains a few functions that are used from individual scripts in the tool

def get_platform():
    # Are we running on Mac or PC?
    system = platform.system()
    if system == 'Darwin':
        mainwork = '/Users/au3406/Desktop/'
    else:
        mainwork = 'C:/Users/au3406/iCloudDrive/Desktop/'
    return mainwork

def map_bearing(x, y, center_x, center_y):
    """
    Calculate the bearing (direction angle) from the center point to a target point.
    Parameters: x (float): X-coordinate of the target point - y (float): Y-coordinate of the target point.
    center_x (float): X-coordinate of the center point.  - center_y (float): Y-coordinate of the center point.
    Returns: float: The bearing angle in degrees, ranging from 0 to 359.
    """
    angle = math.degrees(math.atan2(y - center_y, x - center_x))
    bearing = (90 - angle) % 360
    return bearing

def import_synonyms():
    """
     Import synonyms from an Excel file and store them in a Python dictionary. 
     Returns: dict: A dictionary containing synonyms where keys are keywords and values are synonym keywords.
    """
    xlDic = pd.ExcelFile(get_platform()+'github/scimap/aliasDic.xlsx')
    dict_df = xlDic.parse('keys')
    synonyms = {}
    for index, row in dict_df.iterrows():
        keyw = str(row[0])
        keywa = str(row[1])
        synonyms[keyw] = keywa
    return synonyms

def normalize(values, bounds):
    """
    Normalize a list of values based on specified bounds.
    Parameters: values (list): A list of values to be normalized.
    bounds (dict): A dictionary containing 'desired' and 'actual' bounds, where 'lower' and 'upper' keys are expected.
    Returns:A list of normalized values.
    """
    return [bounds['desired']['lower'] + (x - bounds['actual']['lower']) * (bounds['desired']['upper'] - bounds['desired']['lower']) / (bounds['actual']['upper'] - bounds['actual']['lower']) for x in values]

def adjacent_pairs(seq):
    """
    zip is used to create pairs of adjacent elements in the sequence, and then a list comprehension 
    is used to format the pairs as strings
    """ 
    return [f"{a}-{b}" for a, b in zip(seq, seq[1:])]  

def extract_keywords_from_text(target_text, keyword_set, synonyms):
    """
    Replace punctuation, make lowercase, and tokenize - Remove stopwords using the precomputed set
    Generate adjacent word pairs - Clean and filter keywords - Join the cleaned keywords with a semicolon separator
    """
    target_text = re.sub(r'[-.,]', ' ', target_text).lower()
    text_tokens = word_tokenize(target_text)  
    tokens_without_stopwords = [word for word in text_tokens if word not in stop_words_set]
    all_combinations = adjacent_pairs(tokens_without_stopwords) + tokens_without_stopwords
    all_combinations_clean = [clean_keyword(word, synonyms) for word in all_combinations if word in keyword_set]
    all_combinations_clean = ';'.join(set(all_combinations_clean))
    return all_combinations_clean

def clean_keyword (old_keyword, synonym_dict):
    """
    separating keywords joined by '-' in order to lemmatize and rejoin
    check if part of keyword is a synonym
    finally check if the new composite keyword is a synonym
    """
    composite_keyword = ''
    keyword = old_keyword.replace("-", " ")     # separating keywords joined by '-' in order to lemmatize and rejoin
    for keyword_part in keyword.split(" "):
        if keyword_part != "":
            keyword_part = wnl.lemmatize(keyword_part.lower())
            if (synonym_dict.get(keyword_part, "none")) != 'none':
                keyword_part = synonym_dict.get(keyword_part)              
            if composite_keyword != "":
                composite_keyword = composite_keyword + "-" + keyword_part
            if composite_keyword == "":
                composite_keyword = composite_keyword + keyword_part   
            if (synonym_dict.get(composite_keyword, "none")) != 'none':
                composite_keyword = synonym_dict.get(composite_keyword)
    if composite_keyword != '':
        return composite_keyword

def convert_str_to_list (string): 
    li = list(string.split(";"))
    return li

def clean_str (string):
    return str(string).replace("'", '')

def add_empty_lines(count):
    # Create a function for adding empty lines
    for _ in range(count):
        st.write(' ')