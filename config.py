## Setting paths to files and folders

if (platform.system() == 'Darwin'):
    primary_path = '/Users/flemmingskov/Desktop/'
else:
    primary_path = 'C:/Users/au3406/iCloudDrive/Desktop/'

# update to create list of possible workspaces to each page
list_secondary_paths = ['scimap/modultest/', 'scimap/zoophys/','scimap/wildlife/',  'scimap/cognition/', 'scimap/PLOS/au_biology/']

# variables related to layout and appearance
expander_space = 2  # number of empty lines at the end of the expander