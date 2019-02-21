# This program implements task3 of the project.
# The corpus is segmented into article name, sentences, keywords, lemma, stem and pos_tag.
# The segmented values are stored on a json file named task3.json and pushed to the core named task3.
# Make sure core task3 and user_input are created before running this code.
# Search query is converted to lists of various features and matched against the same of the corpus.

import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import pysolr
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet as wn


def token_word(s):  # Tokenize any sentence and remove stopwords
    token_w = word_tokenize(s)
    token_word_final = []
    stop_words = set(stopwords.words('english'))
    for w in token_w:
        w1 = w.lower()
        if w1 not in stop_words:
            token_word_final.append(w)

    return token_word_final


def token_sent(f):  # Read sentences from file. Extract title, sentence and keywords.
    result = []  # Final List
    sentence = {}
    lemma = {}
    pos = {}
    stem = {}

    article = {}
    head = ""  # Article name
    file = []  # stores entire file as a list of sentences. Easier to access.

    for i in f:
        file.append(i)

    for i in range(0, len(file)):
        l = len(file[i])

        if l == 1:  # If length of string is 1 (\n), Consider next line to be the title of the article.

            if head == "":  # For First article, we just assign the title to head

                head = file[i + 1].rstrip()

                continue

            else:

                for j in sentence:
                    # print(j, sentence[j])
                    article["topic"] = head
                    article["sentence"] = j
                    article["keywords"] = sentence[j]
                    article["lemma"] = lemma[j]
                    article["stem"] = stem[j]
                    article["pos"] = pos[j]

                    result.append(article)
                    article = {}
                sentence = {}

                if i != l:
                    head = file[i + 1]
                    head = head.rstrip()
                continue

        if file[i].rstrip() == head:  # Skip iteration if the next line == head.
            continue
        else:
            # Call token_word function
            sen = file[i].rstrip()
            token_s_final = token_word(sen)
            lemma_words_final = lemma_words(token_s_final)
            stem_words = stemmer(lemma_words_final)
            pos_words = convert_postag(lemma_words_final)

        sentence[sen] = token_s_final
        lemma[sen] = lemma_words_final
        stem[sen] = stem_words
        pos[sen] = pos_words

    # Append Last Article.
    # Can be added to for loop with some modification.

    for j in sentence:
        article["topic"] = head
        article["sentence"] = j
        article["keywords"] = sentence[j]
        article["lemma"] = lemma[j]
        article["stem"] = stem[j]
        article["pos"] = pos[j]

        result.append(article)

    return result


def lemma_words(token_words_final):
    wordnet_lemmatizer = WordNetLemmatizer()
    lemma = []
    for i in token_words_final:
        lemma.append(wordnet_lemmatizer.lemmatize(i))

    # print("Lemmas_word: ",lemma)
    return lemma


def stemmer(lemma):
    port = PorterStemmer()
    stemmed_words = []
    stemmed_words = ([port.stem(i) for i in lemma])

    # print("Stemmed_words: ",stemmed_words)
    return stemmed_words


def pos_tag(lemma_words):
    pos_tagged = nltk.pos_tag(lemma_words)
    # print(pos_tagged)
    return pos_tagged


def convert_postag(lemma_words):
    pos_tagged = pos_tag(lemma_words)

    pos_tagged_mod = []  # Modifed POS Tags
    for i in pos_tagged:
        con = i[1]
        if con.startswith('J'):
            con = 'a'
        elif con.startswith('N'):
            con = 'n'
        elif con.startswith('V'):
            con = 'v'
        elif con.startswith('ADV'):
            con = 'r'
        else:
            con = ''

        i = (i[0], con)
        pos_tag_final = i[0] + '_' + con
        pos_tagged_mod.append(pos_tag_final)
    return pos_tagged_mod


def convert_postag_tuple(lemma_words):  # Returns Tuple
    pos_tagged = pos_tag(lemma_words)

    pos_tagged_mod = []  # Modifed POS Tags
    for i in pos_tagged:
        con = i[1]
        if con.startswith('J'):
            con = 'a'
        elif con.startswith('N'):
            con = 'n'
        elif con.startswith('V'):
            con = 'v'
        elif con.startswith('ADV'):
            con = 'r'
        else:
            con = ''

        i = (i[0], con)
        # j = i[0]+'_'+con
        # pos_tagged_mod.append(j)
        pos_tagged_mod.append(i)
        # print(pos_tagged_mod)
    return pos_tagged_mod


def hyponyms(pos_tagged):
    hypo_list = []
    for i in pos_tagged:
        if str(i[1]) == '':
            continue
        for j in wn.synsets(str(i[0]), str(i[1])):
            sense = str(j)
            # print(sense)
            hypo = j.hyponyms()
            for i in hypo:
                i = str(i)
                hypo_list.append(i.split('\'')[1].split('.')[0])
    # print("Hypo: ",hypo_list[:2])
    return hypo_list


def hypernyms(pos_tagged):
    hyper_list = []
    for i in pos_tagged:
        if str(i[1]) == '':
            continue
        for j in wn.synsets(str(i[0]), str(i[1])):
            sense = str(j)
            # print(sense)
            hyper = j.hypernyms()
            for i in hyper:
                i = str(i)
                hyper_list.append(i.split('\'')[1].split('.')[0])
                # print("HYper:", hyper_list)
    return hyper_list


def meronyms(pos_tagged):
    meronyms_list = []
    for i in pos_tagged:
        if str(i[1]) == '':
            continue
        for j in wn.synsets(str(i[0]), str(i[1])):
            sense = str(j)
            # print(sense)
            mero = j.part_meronyms()
            for i in mero:
                i = str(i)
                meronyms_list.append(i.split('\'')[1].split('.')[0])
                # print("Mero:", meronyms_list)
    return meronyms_list


def holonyms(pos_tagged):
    holo_list = []
    limiter = 0
    for i in pos_tagged:
        if str(i[1]) == '':
            continue
        for j in wn.synsets(str(i[0]), str(i[1])):
            sense = str(j)
            # print(sense)
            holo = j.member_holonyms()
            if limiter <= 5:
                for i in holo:
                    i = str(i)
                    holo_list.append(i.split('\'')[1].split('.')[0])
                    limiter += 1
    return holo_list


def sets_syn(words):
    k = []
    t_w = word_tokenize(words)
    # print(t_w)
    for i in t_w:
        key = wn.synsets(i)
        # print(key)
        for j in key:
            j = str(j)
            k.append(j.split('\'')[1].split('.')[0])
    keys = []
    for i in k:
        if i not in keys:
            keys.append(i)
    return keys


def create_json():
    f = open("rural.txt", "r")
    result_dict = token_sent(f)

    global json
    json1 = json.dumps(result_dict, indent=4)
    f = open("task3.json", "w")
    f.write(json1)
    f.close()


def pysolr_push():
    global json
    solr = pysolr.Solr('http://localhost:8983/solr/task3', timeout=10)
    solr.delete(q='*:*')  # Removes the current content of the core.
    fp = open("task3.json", "r")
    solr.add(json.load(fp))
    fp.close()


def pysolr_push_user_query():
    global json
    solr = pysolr.Solr('http://localhost:8983/solr/user_input', timeout=10)
    solr.delete(q='*:*')  # Removes the current content of the core.
    fp = open("user_input.json", "r")
    solr.add(json.load(fp))
    fp.close()


def user_query():
    user_input = input("\nEnter search query: ")
    user_input_keywords = token_word(user_input)
    user_input_lemma = lemma_words(user_input_keywords)
    user_input_stem = stemmer(user_input_lemma)
    user_input_pos = convert_postag(user_input_lemma)
    user_input_pos_tuple = convert_postag_tuple(user_input_lemma)
    user_input_synset = sets_syn(user_input)

    hyper = hyponyms(user_input_pos_tuple)
    hypo = hyponyms(user_input_pos_tuple)
    mero = meronyms(user_input_pos_tuple)
    holo = holonyms(user_input_pos_tuple)

    user_input_dict = [
        {'sentence': user_input, 'keywords': user_input_keywords, 'lemma': user_input_lemma, 'stem': user_input_stem,
         'pos': user_input_pos, 'hyper': hyper, 'hypo': hypo, 'mero': mero, 'holo': holo, 'synset': user_input_synset}]

    global json

    json1 = json.dumps(user_input_dict, indent=4)
    f = open("user_input.json", "w")
    f.write(json1)
    f.close()

    return user_input_dict


def pysolr_search(query_words, key):
    # Create Connection to Solr
    solr = pysolr.Solr('http://localhost:8983/solr/task3', timeout=10)

    ''' Searching the string '''
    query = "("
    for i in range(0, len(query_words)):
        if i != len(query_words) - 1:
            query = query + "\"" + query_words[i] + "\"" + ","
        else:
            query = query + "\"" + query_words[i] + "\""

    query = query + ")"
    search_keyword = key + ":" + query
    print()
    print(search_keyword, "\n")
    results = solr.search(search_keyword)
    sentences_result = []
    for result in results:
        print("{0}".format(result['sentence'][0]))
        sentences_result.append(result['sentence'][0])

    return results


def main():
    #create_json()
    #pysolr_push()
    user_input_dict = user_query()
    pysolr_push_user_query()

    search_result_keywords = pysolr_search(user_input_dict[0]['keywords'], "keywords")
    search_result_lemma = pysolr_search(user_input_dict[0]['lemma'], "lemma")
    search_result_stem = pysolr_search(user_input_dict[0]['stem'], "stem")
    search_result_pos = pysolr_search(user_input_dict[0]['pos'], "pos")


if __name__ == '__main__':
    main()
