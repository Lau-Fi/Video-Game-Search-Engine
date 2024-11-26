import math, json

import json
import math

from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import regex as re
import collections
import nltk
nltk.download('stopwords')

stops = set(stopwords.words('english'))

headings_list = []

def simpleTokenizor(text):
    global headings_list
    soup = BeautifulSoup(text, 'html.parser')
    paragraphs = soup.find_all('p')
    headings = soup.find_all(re.compile('^h[1]$'))
    headings_list.append(headings)
    #print (headings)
    cleanedTokens = []
    for p in paragraphs:
        cleanedParagraphs = p.get_text()
        #print (cleanedParagraphs)
        reS1 = re.sub("<.+?>|\n", "", str(cleanedParagraphs))
        tokens = word_tokenize(reS1)
        #print(tokens)
        for token in tokens:
            if token not in stops and token != "," and token != " ":
                cleanedTokens.append(token)
        freq = collections.Counter(cleanedTokens)
    return freq




vocabIDCounter = 0
docIDsCounter = 0
vocab = {}
docIDs = {}
postings = {}
htmltexts = {}

for fname in "videogames":
    f = open(fname, "r", encoding='utf-8')
    text = f.read()
    f.close()
    
    docIDs[docIDsCounter] = fname
    htmltexts[docIDsCounter] = text
    tokens = set(simpleTokenizor(text))

    for t in tokens:
        if t in vocab.keys(): 
            vocabID = vocab[t]
        else: 
            vocab[t] = int(vocabIDCounter)
            vocabID = vocabIDCounter
            vocabIDCounter += 1
        
        if vocabID in postings.keys():
            postings[vocabID].append(docIDsCounter)
        else:
            postings[vocabID] = [docIDsCounter]
            
        
    docIDsCounter += 1
cleaned_HTML_headings = []
for h in headings_list:
    cleaned_headings = h[0].get_text()
    cleaned_HTML_headings.append(cleaned_headings)
print(cleaned_HTML_headings)

with open('vocab.txt', 'w') as f: json.dump(vocab, f)
with open('postings.txt', 'w') as f: json.dump(postings, f)
with open('docids.txt', 'w') as f: json.dump(docIDs, f)

with open('vocab.txt', 'r') as f: vocab = json.load(f)
with open('postings.txt', 'r') as f: postings = json.load(f)
with open('docids.txt', 'r') as f: docIDs = json.load(f)

while True:  #loop for user query
    results = {} #the results dictionary, each query word and the pages it appears on.
    query = input("What would you like to query?") 
    if query == "quit": 
        break
    elif query == "":
        break
    
    querylist = query.split(" ") #split the user query by each word into a list
    document_frequencies = [] #create the document frequencies list. A new one each user query. 
    
    for q in querylist: #for every word in the split query list
        word_frequencies = {} #create a dictionary for the count of how many times the query word appears in the html text. Key is the html page name, value is the term frequecny
        results[q] = set() #create a set with each query word having different frequencies for each page it appears on
        if q in vocab: # if the query word is in the vocab corpus as a recognised word...
            vocabID = vocab[q] #the vocab text file with the lookup of the query word will be assigned to vocabID
            documents = postings[str(vocabID)] #documents variable is used to find the word frequencies and results. 
            #It is taken from the posting dictionary with the key of the vocabID.
            
            for d in documents:
                htmltext = htmltexts[int(d)] #gets the HTML text from the documents list.
                word_count = htmltext.lower().split().count(q) #counts the number of individual query words
                word_frequencies[docIDs[str(d)]] = word_count #assigns the count to the dictionary with the file name
                results[q].add(docIDs[str(d)]) #every document we get the document ID and add it to the results back
            document_frequencies.append(word_frequencies) #for every query word we append the freqency of it to a list
            final_tf = {}
            for dict in document_frequencies:
                for key in dict:
                    if key not in final_tf:
                        final_tf[key] = 0
                    final_tf[key] += dict[key]
             
    final = set() #a set is used to store multiple items in a single variable 
    if results: #here we get the overall documents that have have the query word
        for docs in results.values(): #for every document in the results values 
            if not final: #if not in the set 
                final = docs #if final is empty it will get docs and assign to final
            else:
                final = final.intersection(docs) #used to find the common element shared between each query word

    


    n = len(docIDs) #gets overall number of html documents 
    dft = len(final)  #gets all count of all documents with the query word(s)

    print("Documents containing all query words:", final)
    print("Results for each query term:", results)
    print("N (total documents in corpus):", n)
    print("dft (documents containing the term):", dft)
    print("Document frequencies for each query word:", final_tf)
    
    tfidfForEachDoc = []
    
    for freq in final_tf.values():
            if freq > 0:
                tfidf_score = round(math.log(n / dft)*(1+math.log(freq)), 2)
            else:
                tfidf_score = 0
            tfidfForEachDoc.append(tfidf_score)


    print("TF-IDF score for each document:", tfidfForEachDoc)
    print("Total TF-IDF score for the query across all documents:", sum(tfidfForEachDoc))

    final_ranking = final_tf
    
    for i, dic_key in enumerate(final_ranking.keys()):
        if i < len(tfidfForEachDoc):
            final_ranking[dic_key] = tfidfForEachDoc[i]
    print (sorted(final_ranking.items(), key = lambda page: page[1], reverse = True))
# tfidf = log(n/dft)*freq per dictionary entry = tfidf score for each document, and then sort them from highest to lowest when displaying page results.