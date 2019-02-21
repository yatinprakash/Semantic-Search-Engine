# This code extracts all articles in rural.txt as article and sentences and pushes it into solr core task1.
# This can be used to show the number if articles in the file and also can be used to extract the entire article in task 4.
# Make sure the core task1 is created before executing the code.


import pysolr
import json

def article_list():

    result = []

    file = []
    f = open("rural.txt","r")
    for i in f:
        file.append(i)

    article_sentences = []
    len_file = len(file)
    head = ""
    for i in range(0, len_file):

        len_sentence = len(file[i])

        if len_sentence == 1:
            if head == "":
                head = file[i + 1].rstrip()
                continue
            else:
                result.append({"topic":head,"sentences":article_sentences})
                article_sentences = []
                head = file[i + 1].rstrip()
        else:
            if file[i].rstrip() == head:
                continue
            else:
                article_sentences.append(file[i].rstrip())

    result.append({"topic":head,"sentences":article_sentences})

    return result


def pysolr_push(result):

    global json         # Gives "variable accessed before assignment error" if not defined as global.

    json1 = json.dumps(result, indent=4)

    f = open("task1.json", "w")
    f.write(json1)
    f.close()

    solr = pysolr.Solr('http://localhost:8983/solr/task1', timeout=10)
    solr.delete(q='*:*')  # Removes the current content of the core.
    fp = open("task1.json", "r")
    solr.add(json.load(fp))
    fp.close()


def main():

    result = article_list()
    pysolr_push(result)
    print("Articles have been pushed into Task1 core")


if __name__ == '__main__':
    main()







