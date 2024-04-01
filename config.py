## THIS IS THE NEW REBUILDING THING THAT BRANCHED AWAY
## WITH AN EXTRA COMMENT NOW


## Setting paths to files and folders

if (platform.system() == 'Darwin'):
    primary_path = '/Users/au3406/Desktop/'
else:
    primary_path = 'C:/Users/au3406/iCloudDrive/Desktop/'

# update to create list of possible workspaces to each page
list_secondary_paths = ['scimap/zoophys/', 'scimap/land/', 'scimap/rewilding/', 'scimap/cognition/','scimap/sect/',  'scimap/cognition/', 'scimap/PLOS/au_biology/']

# variables related to layout and appearance
expander_space = 1  # number of empty lines at the end of the expander