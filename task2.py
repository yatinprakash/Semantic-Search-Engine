# This program implements task2 of the project.
# The corpus is segmented into sentences and keywords.
# The segmented values are stored on a json file named task2.json and pushed to the core named task2.
# Make sure core task2 and user_input are created before running this code.
# Search query is converted to a keywords list and matched against the keywords of the corpus.

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import pysolr
#import simplejson as json
import subprocess
import json


def token_word(s):   # Tokenize any sentence and remove stopwords
    token_w = word_tokenize(s)
    token_word_final = []
    stop_words = set(stopwords.words('english'))
    for w in token_w:
        w1 = w.lower()
        if w1 not in stop_words:
            token_word_final.append(w)

    return (token_word_final)


def token_sent(f):    # Read sentences from file. Extract title, sentence and keywords.
    result = []       # Final List
    sentence = {}
    article = {}
    head = ""         # Article name
    file = []         # stores entire file as a list of sentences. Easier to access.

    for i in f:
        file.append(i)

    for i in range(0, len(file)):
        l = len(file[i])

        if l == 1:       # If length of string is 1 (\n), Consider next line to be the title of the article.

            if head == "":  # For First article, we just assign the title to head

                head = file[i + 1].rstrip()

                continue

            else:

                for j in sentence:
                    # print(j, sentence[j])
                    article["topic"] = head
                    article["sentence"] = j
                    article["keywords"] = sentence[j]
                    result.append(article)
                    article = {}
                sentence = {}

                if i != l:
                    head = file[i + 1]
                    head = head.rstrip()
                continue

        if file[i].rstrip() == head:    # Skip iteration if the next line == head.
            continue
        else:
            # Call token_word function
            sen = file[i].rstrip()
            token_s_final = token_word(sen)
            sentence[sen] = token_s_final

    # Append Last Article.
    # Can be added to for loop with some modification.

    for j in sentence:
        article["topic"] = head
        article["sentence"] = j
        article["keywords"] = sentence[j]
        result.append(article)

    return result


def create_json():

    f = open("rural.txt", "r")
    result_dict = token_sent(f)

    global json         # Gives "variable accessed before assignment error" if not defined as global.

    json1 = json.dumps(result_dict, indent=4)

    f = open("task2.json", "w")
    f.write(json1)
    f.close()


def pysolr_push():

    global json
    solr = pysolr.Solr('http://localhost:8983/solr/task2', timeout=10)
    solr.delete(q='*:*') # Removes the current content of the core.
    #subprocess.call(['bin/post', '-c', 'task2', 'task2.json'])
    fp = open("task2.json","r")
    solr.add(json.load(fp))
    fp.close()


def pysolr_push_user_query():

    global json
    solr = pysolr.Solr('http://localhost:8983/solr/user_input', timeout=10)
    solr.delete(q='*:*')  # Removes the current content of the core.
    #subprocess.call(['bin/post', '-c', 'user_input', 'user_input.json'])
    fp = open("user_input.json","r")
    solr.add(json.load(fp))
    fp.close()

def user_query():

    user_input = input("\nEnter search query: ")
    user_input_keywords = token_word(user_input)
    user_input_dict = [{'sentence':user_input, 'keywords':user_input_keywords}]
    #print(user_input_dict)
    global json

    json1 = json.dumps(user_input_dict, indent=4)
    f = open("user_input.json", "w")
    f.write(json1)
    f.close()

    return user_input_dict


def pysolr_search(query_words, key):
    # Create Connection to SOlr
    solr = pysolr.Solr('http://localhost:8983/solr/task2', timeout=10)

    ''' Searching the string '''
    query = "("
    for i in range(0, len(query_words)):
        if i != len(query_words) - 1:
            query = query + "\"" + query_words[i] + "\"" + ","
        else:
            query = query + "\"" + query_words[i] + "\""

    query = query + ")"
    search_keyword = key +":"+ query
    print(search_keyword)
    results = solr.search(search_keyword)
    sentences_result = []
    for result in results:
        #print("'{0}'.".format(result['sentence'][0]))
        sentences_result.append(result['sentence'][0])

    return results

'''
def order_result(result, query_words):

    order_list = {}
    for i in result:
        count = 0
        sen = word_tokenize(i)
        for j in sen:
            if j in query_words:
                count = count + 1
        order_list[i] = count

    sort_list = sorted(order_list, key=order_list.get)
    print(sort_list)
'''


def main():
    #create_json()
    #pysolr_push()
    user_input_dict = user_query()
    pysolr_push_user_query()
    search_result = pysolr_search(user_input_dict[0]['keywords'],"keywords")

    print("\nKeyword Search Result:")

    #order_result(search_result,user_input_dict[0]['keywords'])

    for result in search_result:
        print("{0}".format(result['sentence'][0]))


if __name__ == '__main__':
    main()
