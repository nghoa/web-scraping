from bs4 import BeautifulSoup
import pandas as pd
import requests
from pprint import pprint
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
    'User-Agent_9': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0',
    'User-Agent_10': 'Mozilla/5.0 (Windows NT 5.2; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7',
    'User-Agent_11': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36',
    'User-Agent_12': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.17 (KHTML, like Gecko) Chrome/11.0.654.0 Safari/534.17',
    'User-Agent_13': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.16) Gecko/20080716 Firefox/3.07',
    'User-Agent_14': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; sv-SE; rv:1.9.0.18) Gecko/2010020220 Firefox/3.0.18 (.NET CLR 3.5.30729)',
    'User-Agent_15': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18'
}

proxy_increment = 0

def write_to_excel(dataframe):
    # Input: Datei wird im selben Ordner gespeichert unter dem Namen: "output.xlsx"
    dataframe.to_excel('output_amazon_final_full_data.xlsx', sheet_name="amazon")
    return True


"""
    Copy paste die URL's von der Excel in eine neue Tabelle
        - Excel beinhaltet nur die Such-URL
"""
def get_real_amazon_url_from_excel():
    # Input: Spezifierung des Speicherstandortes der Datei
    excel_location = './output.xlsx'   
    df = pd.read_excel(excel_location)
    return df


def get_info_from_amazon(link, agent_number):
    print('Looked up Link: ', link)
    print('Get First Amazon Link -- Agent Number: ', agent_number)
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

    # End Dict
    product_info = {}

    r = requests.get(link, headers=headers)

    if "To discuss automated access to Amazon data please contact" in r.text:
        global proxy_increment
        print("Page %s was blocked by Amazon. Please try using better proxies\n"%link)
        print('Starting Recursion NOW! -- Agent Number: ', proxy_increment)
        proxy_increment += 1
        # Start again from first user agent
        if proxy_increment == 16:
            proxy_increment = 0
            print('----------- Start User Agent from the beginning again! ------------------')
        return get_info_from_amazon(link, proxy_increment)
    else:
        soup = BeautifulSoup(r.text, "lxml")

        # Drei Versionen von Title
        if soup.find('span', {'id': 'productTitle'}) != None:
            title = soup.find('span', {'id': 'productTitle'}).text.strip("\n").strip("\t")
            product_info['title'] = title
        elif soup.find(id='title') != None:
            title = soup.find(id='title').text.strip("\n").strip("\t")
            product_info['title'] = title
        elif soup.find(id='ebooksTitle') != None:
            title = soup.find(id='ebooksTitle').string.strip("\n").strip("\t")
            product_info['title'] = title
        else:
            title = ''
            product_info['title'] = title

        # Drei Versionen von Autoren
        if soup.find('span', {'class': 'contribution'}) != None:
            authors_list = []
            # Fall #1: Autoren sind berühmter und sind in der Amazon DB gelistet
            if len(soup.select('a[class*="contributorNameID"]')) != 0:
                famous_contributors = soup.select('a[class*="contributorNameID"]')
                for famous_contributor in famous_contributors:
                    # Erhalte Liste aller Autoren
                    person_description = famous_contributor.parent.findNext('span').text.strip("\n").strip("\t")
                    if '(Autor)' in person_description:
                        authors_list.append(famous_contributor.text)

            # Fallbeispiel #1: Nur ein Autor
            first_author = soup.find('span', {'class': 'contribution'}).find_previous('a').text.strip("\n").strip("\t")
            contributors = soup.find_all('span', {'class': 'contribution'})
            for contributor in contributors:
                # Erhalte Liste aller Autoren
                if '(Autor)' in contributor.text:
                    author = contributor.find_previous('a').text.strip("\n").strip("\t")
                    if not author == '':
                        authors_list.append(author)
            
            # THE END
            product_info['authors'] = authors_list
        else:
            author = []
            product_info['authors'] = author


        # Rating
        if soup.find('span', attrs={'data-hook': 'rating-out-of-text'}) != None:
            rating = soup.find('span', attrs={'data-hook': 'rating-out-of-text'}).text.split(' ')[0]
            amazon_rated = 'Y'
            product_info['rating'] = rating
            product_info['amazon_rated'] = amazon_rated
        else:
            rating = ''
            amazon_rated = 'N'
            product_info['rating'] = rating
            product_info['amazon_rated'] = amazon_rated

        # Rating Count
        if soup.find(id="acrCustomerReviewText") != None:
            rating_count = soup.find(id="acrCustomerReviewText").text.split(' ')[0]
            product_info['rating_count'] = rating_count
        else:
            rating_count = ''
            product_info['rating_count'] = rating_count

        # Price - Test
        if soup.find('td', {'class': 'a-text-right dp-price-col'}) != None:
            td_prices = soup.find_all('td', {'class': 'a-text-right dp-price-col'})
            for td in td_prices:
                # Nur für den Fall, wenn ein Preis für eine Sonderversion von Kindle (5. November 2015) existiert
                if td.find_previous('td').find('span', {'class': 'a-size-small a-color-base'}) != None:
                    label = td.find_previous('td').find('span', {'class': 'a-size-small a-color-base'}).text
                    erster_preis = td.find('span', {'class': 'a-size-small a-color-price'})
                    zweiter_preis = td.findNext('td').find('span', {'class': 'a-declarative'})
                    dritter_preis = td.findNext('td').findNext('td').find('span', {'class': 'a-declarative'})
                    if 'Kindle' in label:
                        # Nur für den Fall, dass ein "neu" Preis nicht existiert, daher zweiter Preis als Alternative
                        # Zweiter Preis ist gebraucht...
                        if erster_preis != None:
                            kindle_price = erster_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['kindle_price'] = kindle_price
                        elif zweiter_preis != None:
                            kindle_price = zweiter_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['kindle_price'] = kindle_price
                        elif dritter_preis != None:
                            kindle_price = dritter_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['kindle_price'] = kindle_price
                        else:
                            product_info['kindle_price'] = ''
                    if 'Gebundenes' in label:
                        if erster_preis != None:
                            gebunden_book_price = erster_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['gebunden_price'] = gebunden_book_price
                        elif zweiter_preis != None:
                            gebunden_book_price = zweiter_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['gebunden_price'] = gebunden_book_price
                        elif dritter_preis != None:
                            gebunden_book_price = dritter_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['gebunden_price'] = gebunden_book_price
                        else:
                            product_info['gebunden_price'] = ''
                    if 'Taschenbuch' in label:
                        if erster_preis != None:
                            taschenbuch_price = erster_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['taschenbuch_price'] = taschenbuch_price
                        elif zweiter_preis != None:
                            taschenbuch_price = zweiter_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['taschenbuch_price'] = taschenbuch_price
                        elif dritter_preis != None:
                            taschenbuch_price = dritter_preis.text.strip("\n").strip("\t").rstrip().replace(u'\xa0', '')
                            product_info['taschenbuch_price'] = taschenbuch_price
                        else:
                            product_info['taschenbuch_price'] = ''

        # print(soup)
        pprint(product_info)

        return product_info
    

def final_combine_data(df):
    # Einfügen der fehlenden Spalten
    df['TITEL'] = ''
    df['AUTOR_1'] = ''
    df['AUTOR_2'] = ''
    df['AUTOR_3'] = ''
    df['AUTOR_4'] = ''
    df['amazon_rated'] = ''
    df['amazon_stars'] = ''
    df['rating_count'] = ''
    df['taschenbuch_preis'] = ''
    df['buch_preis'] = ''
    df['kindle_preis'] = ''

    # Loopen durch die neue Tabelle (Excel)
    for index, row in df.iterrows():
        amazon_url = row['REAL_URL']

        # Check gegen NaN Werte in Excel
        if not (pd.isnull(amazon_url)):

            # Produktinformationen aus Amazon
            """
                product_info = {
                    'title': title,
                    'authors': authors_list,
                    'rating': rating,
                    'rating_count': rating_count,
                    'amazon_rated': amazon_rated,
                    'kindle_price': kindle_price,
                    'gebunden_price': gebunden_book_price,
                    'taschenbuch_price': taschenbuch_price
                }   
            """
            print('Getting Amazon product info now')
            # Recursion through proxy agent list
            product_info = get_info_from_amazon(amazon_url, proxy_increment)

            if 'title' in product_info:
                df.loc[index, 'TITEL'] = product_info['title']     
            if 'authors' in product_info:
                authors = product_info['authors']
                if len(authors) > 0:
                    for i, author in enumerate(authors, start=1):
                        the_autor = 'AUTOR_' + str(i)
                        df.loc[index, the_autor] = author
                        if i == 4:
                            break
            if 'rating' in product_info:
                df.loc[index, 'amazon_stars'] = product_info['rating']     
            if 'rating_count' in product_info:
                df.loc[index, 'rating_count'] = product_info['rating_count']     
            if 'amazon_rated' in product_info:
                df.loc[index, 'amazon_rated'] = product_info['amazon_rated']     
            if 'kindle_price' in product_info:
                df.loc[index, 'kindle_preis'] = product_info['kindle_price']     
            if 'gebunden_price' in product_info:
                df.loc[index, 'buch_preis'] = product_info['gebunden_price']     
            if 'taschenbuch_price' in product_info:
                df.loc[index, 'taschenbuch_preis'] = product_info['taschenbuch_price']     

            start_pause()
    # return back the new table with REAL URL
    return df
    
def start_pause():
    print('Starting Pause')
    for remaining in range(randrange(10), 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n Pause finished! \n")


# ---------------------------------- Links zum testen --------------------------------------

# Tochter der Sirenen
link_with_full_info = 'https://www.amazon.de/Oceanblue-Tochter-Sirenen-Stefanie-Peisker/dp/3748182147/ref=sr_1_1?dchild=1&qid=1613928215&refinements=p_66%3A9783748182146&s=books&sr=1-1'
# Das Erbe von Osiltee
link_with_two_authors = 'https://www.amazon.de/Das-Erbe-von-Osiltee-Band/dp/3744848760/ref=sr_1_1?dchild=1&qid=1613928198&refinements=p_66%3A9783744848763&s=books&sr=1-1'
link_with_three_authors = 'https://www.amazon.de/Weltenbruch-Laura-Schiereck/dp/375285670X/ref=sr_1_1?dchild=1&qid=1613985878&refinements=p_66%3A9783752856705&s=books&sr=1-1'
# Link ohne Rating
link_without_rating = 'https://www.amazon.de/D%C3%A4monium-pers%C3%B6nlicher-Bericht-Bruno-Sammer-ebook/dp/B0716DZRH3/ref=sr_1_1?dchild=1&qid=1613928641&refinements=p_66%3A9783831109739&s=books&sr=1-1'
link_obama = 'https://www.amazon.de/Ein-verhei%C3%9Fenes-Land-Seiten-Farbbildteil/dp/3328600620/ref=sr_1_1?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dchild=1&keywords=obama&qid=1613998674&s=books&sr=1-1'

kaputter_label_link = 'https://amazon.de/Diarys-Death-Nebel-Morta-Sant-ebook/dp/B017METBO2/ref=sr_1_1?dchild=1&qid=1614096788&refinements=p_66%3A9783738657104&s=books&sr=1-1'

# Testfunktion ohne den gesamten Overhead
# get_info_from_amazon(kaputter_label_link, 1)



def start_crawler():
    start_df = get_real_amazon_url_from_excel()
    product_df = final_combine_data(start_df)
    write_to_excel(product_df)

if __name__ == '__main__':
    start_crawler()
    pass



