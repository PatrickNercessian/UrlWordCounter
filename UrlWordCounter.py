from collections import Counter
import os
import pickle
import traceback

from bs4 import BeautifulSoup
import requests

DEPTH_CONST = 1
COUNTER_DIRECTORY_PATH = 'app/'


def run():
    url = input('Input the desired URL to count word occurrences for: ')
    file_path = '{}/{}.txt'.format(COUNTER_DIRECTORY_PATH, get_file_name_from_url(url))
    
    use_existing_counter = False
    if os.path.exists(file_path):
        use_existing_counter = input('Would you like to use your previous Word Count for this URL? (y/n) ') == 'y'

    if use_existing_counter:
        counter = read_counter_from_file(file_path)  # Use cached counter
    else:
        counter = Counter()
        count_words_in_url(url, counter, set(), DEPTH_CONST)  # Populate new counter for URL
        write_counter_to_file(counter, file_path)  # Cache the serialized counter in file

    command = -1
    while command != 3:
        command = input('\nChoose your command by inputting \"1\", \"2\", or \"3\":\n'
                        '1 - Query by keywords\n'
                        '2 - Display the most common N words\n'
                        '3 - Exit\n')
        if command == '1':
            user_input = input('Input a list of keywords separated by commas (e.g. \"dog, cat, java, santiago\"): ')
            print_keywords_from_counter(user_input.split(','), counter)
        elif command == '2':
            user_input = input('Input the number of most common words you\'d like to display: ')
            print(counter.most_common(int(user_input)))
        elif command == '3':
            break
        else:
            print('You did not enter a valid input. Please input either \"1\", \"2\", or \"3\"')


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

    # Recursively count frequencies for each hyperlink in this webpage until desired depth is reached
    if desired_depth > 0:
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                link_str = link.get('href')

                # ignore links to internal headers and previously visited URLs
                if link_str.startswith('http') and link_str not in visited_urls:
                    count_words_in_url(link_str, counter, visited_urls, desired_depth-1)


def print_keywords_from_counter(keywords: list[str], counter: Counter):
    for keyword in keywords:
        keyword = keyword.strip().lower()
        counter_entry = counter.get(keyword)
        if counter_entry:
            print('\'{}\' occurs {} times.'.format(keyword, counter_entry))
        else:
            print('\'{}\' does not occur at all.'.format(keyword))


def write_counter_to_file(counter: Counter, file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file = open(file_path, 'wb')
    try:
        pickle.dump(counter, file)
    except:
        print('Error during serialization storage')
        traceback.print_exc()
    finally:
        file.close()


def read_counter_from_file(file_path: str):
    file = open(file_path, 'rb')
    try:
        return pickle.load(file)
    except:
        print('Error during serialization retrieval')
        traceback.print_exc()
    finally:
        file.close()


def get_file_name_from_url(url: str):
    return url.replace('/', 'slash')


run()
