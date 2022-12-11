from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import sys
from random import randrange

proxy_dict = {
    'User-Agent_0': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
    'User-Agent_1': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'User-Agent_2': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X; de-AT; rv:1.9.1.8) Gecko/20100625 Firefox/3.6.6',
    'User-Agent_3': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
    'User-Agent_4': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'User-Agent_5': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'User-Agent_6': 'Mozilla/5.0 (Windows NT 5.1; rv:2.0b8pre) Gecko/20101127 Firefox/4.0b8pre',
    'User-Agent_7': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; it-it) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16',
    'User-Agent_8': 'Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00',
    'User-Agent_9': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'
}

proxy_increment = 0

def write_to_excel(dataframe):
    # Input: Datei wird im selben Ordner gespeichert unter dem Namen: "output.xlsx"
    dataframe.to_excel('output.xlsx', sheet_name="test")
    return True


def init_new_df():
    COLUMN_NAMES = [
        'EAN',
        'URL',
    ]

    df = pd.DataFrame(columns=COLUMN_NAMES)
    return df

"""
    Copy paste die URL's von der Excel in eine neue Tabelle
        - Excel beinhaltet nur die Such-URL
"""
def get_amazon_url_from_excel():
    # Input: Spezifierung des Speicherstandortes der Datei
    excel_location = './EANwURL_excel_Verweise.xlsx'   
    df = pd.read_excel(excel_location, na_filter=True)
    new_df = init_new_df()
    for index, row in df.iterrows():
        isbn = row['EAN']
        url = row['URL']
        new_df.loc[index] = [isbn, url]
    return new_df

def get_real_amazon_url(df):
    # Einfügen einer leeren Spalte
    df['REAL_URL'] = ''
    for index, row in df.iterrows():
        url = row['URL']
        print('EAN Link: ', url)
        if not (pd.isnull(url)):
            # HTTP REQUEST - Amazon      
            # Recursion through proxy_increment
            href_link = get_first_amazon_link(url, proxy_increment)
            # prevent NoneType
            if href_link:
                amazon_link = 'https://amazon.de' + href_link
                df.loc[index, 'REAL_URL'] = amazon_link
                print('Richtiger Amazon Link: ', amazon_link)
            else:
                print('Error in HREF-Link Erstellung')
        
            start_pause()

    # return back the new table with REAL URL
    return df

def get_first_amazon_link(link, agent_number):
    print('Get First Amazon Link -- Agent Number: ', agent_number)
    # Prevent Captcha - changing headers information - second link
    # Reference:
    # https://www.scrapehero.com/tutorial-how-to-scrape-amazon-product-details-using-python-and-selectorlib/
    agent = 'User-Agent_' + str(agent_number)
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': proxy_dict[agent],
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    r = requests.get(link, headers=headers)
    
    if "To discuss automated access to Amazon data please contact" in r.text:
        global proxy_increment
        print("Page %s was blocked by Amazon. Please try using better proxies\n"%link)
        print('Starting Recursion NOW! -- Agent Number: ', proxy_increment)
        proxy_increment += 1
        # Start again from first user agent
        if proxy_increment == 10:
            proxy_increment = 0
            print('----------- Start User Agent from the beginning again! ------------------')
        return get_first_amazon_link(link, proxy_increment)
        
    else:
        soup = BeautifulSoup(r.text, "lxml")
        title_href_class = 'a-link-normal a-text-normal'
        for a in soup.find_all('a', {'class' : title_href_class}, href=True):
            new_link = a['href']
            return new_link

def start_pause():
    print('Starting Pause')
    for remaining in range(randrange(15), 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n Pause finished! \n")


def start_crawler():
    start_df = get_amazon_url_from_excel()
    new_url_df = get_real_amazon_url(start_df)
    write_to_excel(new_url_df)

if __name__ == '__main__':
    start_crawler()
