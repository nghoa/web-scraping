from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import sys
from pprint import pprint
from random import randrange

proxy_increment = 0
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
    'User-Agent_9': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0',
    'User-Agent_10': 'Mozilla/5.0 (Windows NT 5.2; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7',
    'User-Agent_11': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36',
    'User-Agent_12': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.17 (KHTML, like Gecko) Chrome/11.0.654.0 Safari/534.17',
    'User-Agent_13': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.16) Gecko/20080716 Firefox/3.07',
    'User-Agent_14': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; sv-SE; rv:1.9.0.18) Gecko/2010020220 Firefox/3.0.18 (.NET CLR 3.5.30729)',
    'User-Agent_15': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18'
}

headers_2 = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'https://www.goodreads.com/',
    'Upgrade-Insecure-Requests': 1
}

def write_to_excel(dataframe):
    # Input: Datei wird im selben Ordner gespeichert unter dem Namen: "output.xlsx"
    dataframe.to_excel('output_goodreads_final.xlsx', sheet_name="goodreads")
    return True

def get_data_from_excel():
    # Input: Spezifierung des Speicherstandortes der Datei
    excel_location = './data/output_amazon_final_full_data.xlsx'   
    df = pd.read_excel(excel_location)
    return df


def get_author_url(EAN):
    agent = 'User-Agent_' + str(proxy_increment)
    print('Looked up EAN: ', EAN)
    print('------------- Agent Number: %s ---------------' %proxy_increment)

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': proxy_dict[agent],
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.goodreads.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    query = '/search?utf8=%E2%9C%93&query=' + str(EAN) 
    link = 'https://www.goodreads.com' + query
    r = requests.get(link, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    a_authors = soup.find_all('a', {'class': 'authorName'})

    # print('So many Authors: ', len(a_authors))

    return a_authors    


def get_author_info(link):
    agent = 'User-Agent_' + str(proxy_increment)
    print('Looked up Author Link: ', link)
    print('------------- Agent Number: %s ---------------' %proxy_increment)

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': proxy_dict[agent],
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.goodreads.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    r = requests.get(link, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    author_info = {}

    # Generell Review Information
    review_infos = soup.find('div', {'class': 'hreview-aggregate'})
    # Get Detailed infos from review_info box

    if review_infos.find('span', attrs={'itemprop': 'ratingValue'}) != None:
        author_info['rating_avg'] = review_infos.find('span', attrs={'itemprop': 'ratingValue'}).text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '').lstrip().replace(',', '').replace('.', '')
    else:
        author_info['rating_avg'] = int()
    if review_infos.find('span', attrs={'itemprop': 'ratingCount'}) != None:
        author_info['rating_count'] = review_infos.find('span', attrs={'itemprop': 'ratingCount'}).text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '').lstrip().replace(',', '').replace('.', '')
    else:
        author_info['rating_count'] = int()
    if review_infos.find('span', attrs={'itemprop': 'reviewCount'}) != None:
        author_info['review_count'] = review_infos.find('span', attrs={'itemprop': 'reviewCount'}).text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '').lstrip().replace(',', '').replace('.', '')
    else:
        author_info['review_count'] = int()

    author_id = link.split('/')[-1].split('.')[0]
    link_variable = '/author_followings?id={}&method=get'.format(author_id)
    followers_check = soup.find('a', attrs={'href': link_variable}).parent.parent.nextSibling.text
    followers_string = soup.find('a', attrs={'href': link_variable}).text
    # test_follower = soup.find('div', {'class': 'bigBoxContent containerWithHeaderContent'}).text
    if 'None yet' in followers_check:
        author_info['follower_count'] = 0
    else:
        author_info['follower_count'] = followers_string.split(' ')[-1].replace('(', '').replace(')', '').strip("\n").strip("\t").rstrip().replace(u'\xa0', '').lstrip().replace(',', '').replace('.', '')

    # End Data
    pprint(author_info)
    return author_info


def final_combine_data(df):
    COLUMN_NAMES = ['EAN', 'Autor', 'Follower Anzahl', 'Average Rating', 'Rating Anzahl', 'Reviews Anzahl']
    new_df = pd.DataFrame(columns=COLUMN_NAMES)

    # All rows from Full dataset Excel
    for index, row in df.iterrows():
        if not pd.isna(row['EAN']):
            isbn = int(row['EAN'])
            a_authors = get_author_url(isbn)
            
            for a_author in a_authors:
                author_link = a_author['href']
                print('Author Link: ', author_link)
                author_name = a_author.text
                print('Author Name: ', author_name)

                author_info = get_author_info(author_link)
                new_df = new_df.append({
                    'EAN': isbn, 
                    'Autor': author_name,
                    'Follower Anzahl': int(author_info['follower_count']),
                    'Average Rating': float(author_info['rating_avg']), 
                    'Rating Anzahl': int(author_info['rating_count']), 
                    'Reviews Anzahl': int(author_info['review_count'])
                    }, ignore_index=True)

    return new_df


# --------------------- Test EAN's ------------------------------------

ean_with_one_author = '9783752867435'
ean_with_two_authors = '9783746014630'
ean_with_three_authors = '9783752856705'
ean_with_four_authors = '9783750422230'

link_to_author_no_follower = 'https://www.goodreads.com/author/show/18293909.Heike_Bicher_Seidel'
link_to_author_with_follower = 'https://www.goodreads.com/author/show/16521541.Devon_Wolters'
link_with_bug = 'https://www.goodreads.com/author/show/14670647.Lars_Hannig'
link_with_another_bug = 'https://www.goodreads.com/author/show/16197994.Tessa_Millard'

# get_author_url(ean_with_four_authors)
# get_author_info(link_with_another_bug)


def start_crawler():
    start_df = get_data_from_excel()
    output_df = final_combine_data(start_df)
    write_to_excel(output_df)


if __name__ == '__main__':
    start_crawler()
    pass