import json
import getpass
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# set a PATH to your bookmark repository
# if you use other os, please modify PATH
CHROME_BOOKMARK_PATH = (
    '/Users/{username}/Library/Application Support/'
    'Google/Chrome/Default/Bookmarks'
).format(username=getpass.getuser())

# set a dictionary site name
DICTIONARY_SITE = 'Weblio'

# get bookmarks from bookmark_data
def get_bookmarks(bookmark_data, folder_location_number):
    return bookmark_data['roots']['bookmark_bar']['children'][folder_location_number]['children']

# get dictionary-type data of your bookmarks
def get_chrome_bookmark_data() -> dict:
    with open(CHROME_BOOKMARK_PATH) as f:
        return json.load(f)

# define a function that extracts a url from each bookmark
def get_dictionary_site_url(bookmark):
    if DICTIONARY_SITE in bookmark['name'] and '意味・' in bookmark['name']:
        return bookmark['url']

def extract_words_meanings_from_html_files(df: pd.DataFrame, url_list_filtered: list):
    i = 0
    while i < len(url_list_filtered):
        # analyse html files
        response = requests.get(url_list_filtered[i])
        soup = BeautifulSoup(response.content, "html.parser")
        # extract meanings by setting the class
        elements = soup.select(".content-explanation.ej")
        # extract only alphabets from the title, which is the word
        alphabet = re.compile('[a-z,A-Z]+')
        word = ' '.join(alphabet.findall(soup.title.text)).replace(DICTIONARY_SITE, '')
        # store the words and meanings in a dataframe
        if len(elements) > 0:
            df = df.append([[word, elements[0].text]], ignore_index=True)
        i += 1
    return df


def main():
    #### get bookmark info ####
    bookmark_data = get_chrome_bookmark_data()

    # locate your wanted bookmarks /////This depends on the structure of your bookmarks.
    folder_location_number = 0
    bookmarks = get_bookmarks(bookmark_data, folder_location_number)

    ### get the urls of the bookmarks ####
    # apply the function to the whole bookmarks
    url_list = list(map(get_dictionary_site_url,bookmarks))
    # print(url_list)

    # filter out None from the url list.
    url_list_filtered = list(filter(None, url_list))

    #### extract words and meanings from html files ####
    df = pd.DataFrame()
    df = extract_words_meanings_from_html_files(df, url_list_filtered)
    # export the dataframe as a csv file
    df.to_csv(DICTIONARY_SITE + '_word_list.csv')

if __name__ == "__main__":
    main()
