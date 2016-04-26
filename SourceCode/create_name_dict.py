from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.request
import pickle
import sys
sys.setrecursionlimit(10**6)

# Get Main Page That Lists All Names By Usage
url = 'http://www.behindthename.com/names/list'
response = urllib.request.urlopen(url)
nameHTML = response.read()
response.close()

# Get Beautiful Soup Module to parse the webpage
soup = BeautifulSoup(nameHTML, 'html.parser')

# After looking at page source, we know where the names appear, and
# extract them
name_links = soup.find_all('span', class_='heavy')

# Get urls for all name by region/category
urls = []
for link in name_links:
    urls.append(link.contents[0]['href'])

# Save base url for appending region/category urls to
base_url = 'http://www.behindthename.com/'

# Dictionary to store region, names key-value pairs
region_name_dict = defaultdict(set)
name_region_dict = defaultdict(set)


def has_fuzzy_key(key):
    '''
    Searches if similar key already in name map. Avoids
    adding subregion duplicates (i.e. East-Aftrica to Africa;
    Africa should already contain names from East-Africa)
    '''
    for name in region_name_dict:
        if name in key:
            return True
    return False


def to_exclude(category):
    '''
	Determines if a category should be excluded
	from adding to dictionary of regions/category
	name mappings
    '''
    exclude = {
    	'history', 'astronomy', 'popular-culture', 'hinduism',
    	'mythology', 'theology', 'judeo-christian-legend',
    	'all-biblical', 'literature', 'ancient', 'medieval'
    }

    if category in exclude or 'mythology' in category:
    	return True
    return False

def parse_names(url):
    '''
    Parses a web page to find names and country
    (or region) of origin for each name. Returns
    a map of country: name_list key-value pairs
    '''
    region = url.split('/')[-1]
    if not has_fuzzy_key(region) and not to_exclude(region):
        response = urllib.request.urlopen(url)
        html = response.read()
        response.close()
        soup = BeautifulSoup(html, 'html.parser')
        names = soup.find_all('div', class_='browsename')
        for name in names:
            region_name_dict[region].add(name.a.contents[0].lower())
            name_region_dict[name.a.contents[0].lower()].add(region)

# add all names to their region key in name_dict
for url in urls:
    parse_names(base_url + url)


# write region_name_dict to pickle file for serialized storage
with open('region-names.pkl', 'wb') as f:
    pickle.dump(region_name_dict, f)

with open('names-region.pkl', 'wb') as f:
	pickle.dump(name_region_dict, f)
