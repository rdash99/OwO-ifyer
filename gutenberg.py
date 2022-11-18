import errno
import glob
import os
import zipfile
from urllib.request import urlretrieve
import multiprocessing
from os import listdir
from os.path import isfile, join

import bs4
import requests

def downloadAll(urls_to_books):
    if not os.path.exists('logs/'):
        try:
            os.makedirs('logs/')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    #for url in urls_to_books[url_num:]:
    print('Downloading books...')
    print('Total number of books to download: ' + str(len(urls_to_books)))
    
    chunks = chunk(urls_to_books, 250)
        
    processes = []

    chunkLength = len(chunks)
    i = 0
    for item in chunks:
        p = multiprocessing.Process(target=download, args=(item,))
        p.name = str(i)
        p.start()
        processes.append(p)
        i += 1
    print('Processes started: ' + str(len(processes)))

def chunk(lst, amt):
    lstChunk = []
    for i in range(0, len(lst), amt):
        lstChunk.append(lst[i: i + amt])
    return lstChunk

def download(url):
    file_num = 0
    url_num = 0
    log_num = 0
    try:
        with open(multiprocessing.current_process().name + '.txt', 'r') as log:
            log_num = int(log.read())
        log.close()
        print('Log file found. Starting from book # ' + str(log_num))
        url = url[log_num:]
    except:
        pass
    for item in url:
        dst = 'books/' + item.split('/')[-1].split('.')[0].split('-')[0]

        """ with open('logfile.log', 'w') as f:
            f.write('Unzipping file #' + str(url_num) + ' ' + dst + '.zip' + '\n') """
        remaining_download_tries = 15

        while remaining_download_tries > 0 :
            try:
                urlretrieve(item, dst + '.zip')
                file_num += 1
                url_num += 1
                print(url_num)

                """ with zipfile.ZipFile(dst + '.zip', "r") as zip_ref:
                    try:
                        zip_ref.extractall("books/")
                        #print(str(url_num) + ' ' + dst + '.zip ' + 'unzipped successfully!')
                        except NotImplementedError:
                        print(str(url_num) + ' Cannot unzip file:', dst) """

                #os.remove(dst + '.zip')
            except:
                print('Chunk ' + multiprocessing.current_process().name + ' encountered an issue downloading file #' + str(url_num) + ' ' + dst + '.zip')
                remaining_download_tries = remaining_download_tries - 1
                with open ('logs/' + str(multiprocessing.current_process().name) + '.txt', 'w') as f:
                    f.write(str(file_num))
                f.close()
                if remaining_download_tries == 0:
                    print('Chunk ' + multiprocessing.current_process().name + ' failed at file #' + str(url_num) + ' ' + dst + '.zip')
                    exit()
                else:
                    continue
    print('Chunk ' + multiprocessing.current_process().name + ' finished!')

def decompressAll():
    onlyfiles = [f for f in listdir("./books") if isfile(join("./books", f))]
    here = os.path.dirname(os.path.abspath(__file__))
    print('Unzipping books...')
    print('Total number of files to decompress: ' + str(len(onlyfiles)))
    
    chunks = chunk(onlyfiles, 250)
        
    processes = []

    chunkLength = len(chunks)
    i = 0
    for item in chunks:
        p = multiprocessing.Process(target=decompress, args=(item,))
        p.name = str(i)
        p.start()
        processes.append(p)
        i += 1
    print('Processes started: ' + str(len(processes)))

def decompress(files):
    for file in files:
        with zipfile.ZipFile(file, "r") as zip_ref:
            try:
                zip_ref.extractall("books/")
                print(file + ' unzipped successfully!')
                os.remove(file)
            except NotImplementedError:
                print('Cannot unzip file:', file)
    print('Chunk ' + multiprocessing.current_process().name + ' finished!')

def main():

    if not os.path.exists('books/'):
        try:
            os.makedirs('books/')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # STEP 1. BUILD A LIST OF URLS

    urls_to_books = []

    if not os.path.exists('urls_to_books.txt'):

        page_w_books_url = 'http://www.gutenberg.org/robot/harvest?filetypes[]=txt&langs[]=en'

        while 1 == 1:

            is_last_page = False

            print('Reading page: ' + page_w_books_url)

            page_w_books = requests.get(page_w_books_url, timeout=20.0)

            if page_w_books:
                page_w_books = bs4.BeautifulSoup(page_w_books.text, "lxml")
                urls = [el.get('href') for el in page_w_books.select('body > p > a[href^="http://aleph.gutenberg.org/"]')]
                url_to_next_page = page_w_books.find_all('a', string='Next Page')

                if len(urls) > 0:
                    urls_to_books.append(urls)

                    if url_to_next_page[0]:
                        page_w_books_url = "http://www.gutenberg.org/robot/" + url_to_next_page[0].get('href')
                else:
                    is_last_page = True

            if is_last_page:
                break

        urls_to_books = [item for sublist in urls_to_books for item in sublist]

        # Backing up the list of URLs
        with open('urls_to_books.txt', 'w') as output:
            for u in urls_to_books:
                output.write('%s\n' % u)

    # STEP 2. DOWNLOAD BOOKS

    # If, at some point, Step 2 is interrupted due to unforeseen
    # circumstances (power outage, lost of internet connection), replace the number
    # (value of the variable url_num) below with the one you will find in the logfile.log
    # Example
    #       logfile.log : Unzipping file #99 books/10020.zip
    #       the number  : 99

    if os.path.exists('urls_to_books.txt') and len(urls_to_books) == 0:
        with open('urls_to_books.txt', 'r') as f:
            urls_to_books = f.read().splitlines()
    downloadAll(urls_to_books)
    #decompressAll()

     


if __name__ == '__main__':
    """
    The main function is called when gutenberg.py is run from the command line
    """

    main()
    
