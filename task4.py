import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import pysolr
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet as wn
import operator


def token_word(s):
    token_w = word_tokenize(s)
    token_word_final = []
    stopWords = set(stopwords.words('english'))
    for w in token_w:
        w1 = w.lower()
        if w1 not in stopWords:
            token_word_final.append(w)

    return token_word_final


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


def pos_tag(lemma):
    pos_tagged = nltk.pos_tag(lemma)
    # print(pos_tagged)
    return pos_tagged


def convert_postag(lemma_words):  # Returns Tuple
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


def convert_postag1(lemma_words):  # Returns word_tag
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
        elif con.startswith('ADV') or con.startswith('R'):
            con = 'r'
        else:
            con = ''

        # i = (i[0], con)
        j = i[0] + '_' + con
        pos_tagged_mod.append(j)
        # pos_tagged_mod.append(i)
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
    #print("Hypo: ", hypo_list[:2])
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


def pysolr_conn():
    solr = pysolr.Solr('http://localhost:8983/solr/task3', timeout=10)
    return solr


def pysolr_search(query_words, stage):
    # Create Connection to SOlr
    solr = pysolr_conn()

    ''' Searching the string '''
    query = "("
    for i in range(0, len(query_words)):
        if i != len(query_words) - 1:
            query = query + "\"" + query_words[i] + "\"" + ","
        else:
            query = query + "\"" + query_words[i] + "\""

    query = query + ")"
    search_keyword = stage + query
    #print(stage, search_keyword)
    results = solr.search(search_keyword)
    sentences_result = []
    # for result in results:
    # print("'{0}'.".format(result['sentence']))
    #   sentences_result.append(result['sentence'])

    return results


def weight(result, search_list, stage):
    counting = []

    for i in result:

        query_output = i[stage]
        query_output_lower = []

        for k in query_output:
            query_output_lower.append(k.lower())
            count = 0

            for j in search_list:

                if j.lower() in query_output_lower:
                    count = count + 1

        counting.append((count, i['sentence'][0]))  # ,i[stage]))

    #for i, j in counting:
    #    print(i, j)

    return counting


def weight_count(count_1, result):
    for i, j in count_1:
        if j in result:
            result[j] = result[j] + i
        else:
            result[j] = i

    return result


def main():
    user_input = input("Enter Sentence: ")
    tokenized_user_input = token_word(user_input)
    lemma_user_input = lemma_words(tokenized_user_input)
    stem_user_input = stemmer(lemma_user_input)
    pos_user_input_original = pos_tag(lemma_user_input)
    pos_user_input_tuple = convert_postag(lemma_user_input)
    pos_user_input_str_tag = convert_postag1(lemma_user_input)
    syn_user_inp = sets_syn(user_input)

    hyper = hyponyms(pos_user_input_tuple)
    hypo = hyponyms(pos_user_input_tuple)
    mero = meronyms(pos_user_input_tuple)
    holo = holonyms(pos_user_input_tuple)

    #print(hypo)

    result = {}

    #print("\nPysolr Search:")
    #print("Keywords\n")
    stage = "keywords:"
    search_result = pysolr_search(tokenized_user_input, stage)
    #print('\n\n\n', search_result)
    keywords_weight = weight(search_result, tokenized_user_input, "keywords")

    # weight1(search_result,tokenized_user_input)

    #print("\nPysolr Search:")
    #print("Synset\n")
    stage = "keywords:"
    search_result = pysolr_search(syn_user_inp, stage)
    syn_weight = weight(search_result, syn_user_inp, "keywords")
    # weight1(search_result,tokenized_user_input)



    #print("\nPysolr Search:")
    #print("Lemma\n")
    stage = "lemma:"
    search_result = pysolr_search(lemma_user_input, stage)
    lemma_weight = weight(search_result, lemma_user_input, "lemma")
    # weight1(search_result, tokenized_user_input)

    #print("\nPysolr Search:")
    #print("Stem\n")
    stage = "stem:"
    search_result = pysolr_search(stem_user_input, stage)
    stem_weight = weight(search_result, stem_user_input, "stem")
    # weight1(search_result, tokenized_user_input)

    #print("\nPysolr Search:")
    #print("POS\n")
    stage = "pos:"
    #print(pos_user_input_original)
    search_result = pysolr_search(pos_user_input_str_tag, stage)
    pos_weight = weight(search_result, pos_user_input_str_tag, "pos")
    # weight1(search_result, tokenized_user_input)

    result = weight_count(keywords_weight, result)
    result = weight_count(syn_weight, result)
    result = weight_count(lemma_weight, result)
    result = weight_count(stem_weight, result)
    result = weight_count(pos_weight, result)

    #print('\n\nResult:')


    #print(result)
    #for i in result:
     #   print(result[i], i)

    sorted_result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
    #print(sorted_x)

    count = 0

    final_sorted_result = []
    for i,j in sorted_result:
        final_sorted_result.append((i,j))
        count = count + 1
        if count == 10:
            break



    print()
    print("Best semantic search results:\n")
    for i,j in final_sorted_result:
        print(j,'\t', i,'\n')




    # Query too long error - Holo
    '''
    print("\nPysolr Search:")
    print("Hyper\n")
    stage = "keywords:"
    search_result = pysolr_search(hyper, stage)
    weight(search_result, hyper, "keywords")

    print("\nPysolr Search:")
    print("Hypo\n")
    stage = "keywords:"
    search_result = pysolr_search(hypo, stage)
    weight(search_result, hypo, "keywords")

    print("\nPysolr Search:")
    print("Mero\n")
    stage = "keywords:"
    #print(mero)
    search_result = pysolr_search(mero, stage)
    weight(search_result, mero, "keywords")


    print("\nPysolr Search:")
    print("Holo\n")
    stage = "keywords:"
    search_result = pysolr_search(holo, stage)
    weight(search_result, holo, "keywords")
    '''


if __name__ == '__main__':
    main()
