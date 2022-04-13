import argparse
import traceback
from collections import Counter
from os.path import exists
import requests
import pickle

from bs4 import BeautifulSoup

DEPTH_CONST = 2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u', help='The URL to get word counts from')
    parser.add_argument('--most-common', '-mc', nargs='?', const=1, type=int, help='The number of most common words to display')
    parser.add_argument('--keywords', '-k', nargs='*', help='A list of keywords to query the number of occurrences for')
    return parser.parse_args()


def run():
    args = parse_args()
    if args.url:  # if new URL specified
        counter = Counter()
        visited_urls = set()
        count_words_in_url(args.url, counter, visited_urls, DEPTH_CONST)
        write_counter_to_file(counter)
    elif exists('CounterFile.txt'):  # else if counter cache exists
        counter = read_counter_from_file()
    else:
        raise Exception('No URL specified and no cached counter detected. Please use the --url <URL> flag.')

    # Display frequency of each keyword input
    if args.keywords:
        for keyword in args.keywords:
            keyword = keyword.lower()
            counter_entry = counter.get(keyword)
            if counter_entry:
                print('\'{}\' occurs {} times.'.format(keyword, counter_entry))
            else:
                print('\'{}\' does not occur at all.'.format(keyword))

    # Display the frequencies of 'n' most common words
    if args.most_common:
        print(counter.most_common(args.most_common))


def count_words_in_url(url: str, counter: Counter, visited_urls: set, desired_depth: int):
    print('Visiting URL: {}'.format(url))
    visited_urls.add(url)
    try:
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    except:
        traceback.print_exc()
        return

    # Count frequencies of words (case-insensitive) in this webpage
    site_text = soup.get_text(' ')
    list_of_words = site_text.lower().split()
    counter.update(list_of_words)

    if desired_depth > 0:
        for link in soup.find_all('a'):  # Repeat for all hyperlinks in this webpage
            if link.has_attr('href'):
                link_str = link.get('href')

                # ignore links to internal headers and previously visited URLs
                if link_str.startswith('http') and link_str not in visited_urls:
                    count_words_in_url(link_str, counter, visited_urls, desired_depth-1)


def write_counter_to_file(counter: Counter):
    file = open('CounterFile.txt', 'wb')
    try:
        pickle.dump(counter, file)
    except:
        print('Error during serialization storage')
        traceback.print_exc()
    finally:
        file.close()


def read_counter_from_file():
    file = open('CounterFile.txt', 'rb')
    try:
        return pickle.load(file)
    except:
        print('Error during serialization retrieval')
        traceback.print_exc()
    finally:
        file.close()


run()
