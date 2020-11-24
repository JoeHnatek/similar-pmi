"""
Written by: Joseph Hnatek
Date: Nov. 10, 2020

=== OVERALL ===
This program will take in news text to see the similarity between words.
We use a bigram model to handle the two words: target and context.
This program will output formatted data for the cosine and PMI value along with counts.

=== EXAMPLE ===
python3 similiar-pmi.py 2 ./PA4-News-2011 word-pairs.txt
PA 4 computing similarity from a word by word PMI co-occurrence matrix, programmed by Joseph Hnatek.
Tokens = 47,406,270, Types = 2,400,000, Window = 2
0.12657 line cord 11684 196 0 0.00000
0.35237 line queue 11684 101 0 0.00000
0.24560 line text 11684 2235 0 0.00000
0.25413 car automobile 13018 398 0 0.00000
0.05990 swedish finnish 874 226 0 0.00000

=== ALGORITHM ===
Take in the data and process it so we only get alphanumeric and lower case it.
Gather the counts of single unique words.
Gather the word pairs from our 'word-pairs.txt'
After we get the word pairs, we gather the bigrams from the news data.
We then create a PMI matrix of |V| x |V|.
We then calculate the PMI of the word pairs.
Finally, compute the Cosine values and output to the user.
"""


import sys
import os
import re
import math
import numpy

def preProcessing(filepath):
    """
    Preprocess the data so we can handle it sentence by sentence.
    """
    newsList = []
    data = ""

    directory = filepath
    for filename in os.listdir(filepath):   # Read each file in the directory.
        #print(filename)
        if filename.endswith(".txt"):
            with open(filepath + '/' + filename, 'r') as file:
                data = file.read()

                data = data.lower()

                data = re.sub(r'([^A-Za-z0-9\n]+)', r' ', data) # Leave only the alphanumerical chars
                data = data.split('\n')

                for x in range(len(data)):
                    data[x] = data[x].strip()

                if(data[-1] == " " or data[-1] == ''):  # Remove "bigrams" from the list if there is only a unigram in it.
                    del data[-1]

                for line in data:
                    newsList.append(line.split())   # Append the bigram to the newsList.

                data = ""

    return newsList


def getCount(data):
    """
    Get the counts of the words.
    """
    counts = {}
    for line in data:
        for word in line:
            if word not in counts:
                counts[word] = 1
            else:
                counts[word] += 1

    return counts

def getTotalCount(data):
    """
    Get the total words from our vocab list.
    """
    count = 0

    for key, value in data.items():
        count += value

    return count

def getWordPairs(wordPairsFile):
    """
    Gather the word pairs from the 
    """
    wordPairs = []

    with open(wordPairsFile) as file:
        data = file.readlines()

        for line in data:
            line = line.split()
            if len(line) != 0:
                wordPairs.append(line)

    return wordPairs

def bigram(data, windowSize):
    """
    Creating the bigram with the specified window size.
    """
    STEP = 1
    N_GRAM = 2

    newTokens = []
    temp = []

    for line in data:
        for i in range(0, len(line) - windowSize + 1):
            if windowSize == 5:
                for j in range(windowSize - 1):
                    temp.append([line[i], line[i+j+1]])
            else:
                temp.append(line[i : i + N_GRAM])
            
        newTokens.extend(temp)
        temp = []

    bigrams = []

    for x in range(len(newTokens)):
        if len(newTokens[x]) == 2:
            bigrams.append(newTokens[x])
    return bigrams

def getCoWordCount(data):
    """
    Gather how many times words co-occur with eachother.
    """
    coWordCount = {}

    for coWord in data:
        target = coWord[0]
        context = coWord[1]

        if target not in coWordCount:
            coWordCount[target] = {}
        
        if context not in coWordCount[target]:
            coWordCount[target][context] = 1
        else:
            coWordCount[target][context] += 1
    
    return coWordCount


def createMatrix(data):
    """
    Create our massive matrix.
    """
    dim = len(data)
    pmiMatrix = numpy.zeros((100000, 100000), float) # target (row) x context (col)
    PMI_INDEX = {}
    INVERSE = {}
    index = 0
    print("Matrix created...")

    for word in data:
        PMI_INDEX[word] = index
        INVERSE[index] = word
        index += 1

    return pmiMatrix, PMI_INDEX, INVERSE

def calculatePMI(data, singleWordsCounts, totalCount, pmiMatrix, PMI_INDEX):
    print("Calculating PMI...")

    for target in data:
        for context in data[target]:
            p = data[target][context] / totalCount  # Calculate the probability of co-occurance word

            p1 = singleWordsCounts[target] / totalCount # Calculate the probability of the single target word.
            p2 = singleWordsCounts[context] / totalCount    # Calculate the probability of the single context word.

            if PMI_INDEX[target] > 99998 or PMI_INDEX[context] > 99998:
                break

            pmiMatrix[PMI_INDEX[target]][PMI_INDEX[context]] = math.log2(p/(p1*p2)) # Calc. the log2 value for PMI
    
    print("Done.")
    return pmiMatrix


def computeCosine(pmiMatrix, vocabList, wordPairs, coWordCount, INVERSE):
    """
    Compute the cosine for each word pair in our file.
    """
    num = 0
    den = 0
    sumTarget = 0
    sumContext = 0
    cosine = {}

    for target, context in wordPairs:
        num = 0
        den = 0
        sumTarget = 0
        sumContext = 0

        if target in vocabList and context in vocabList:
            for word in vocabList:

                try:
                    tmp1 = coWordCount[target][word]
                except:
                    tmp1 = 0
                try:
                    tmp2 = coWordCount[context][word]
                except:
                    tmp2 = 0
                num += tmp1*tmp2
                sumTarget += tmp1**2
                sumContext += tmp2**2
                
            den = math.sqrt(sumTarget) * math.sqrt(sumContext)

        if den == 0:
            result = -9999
        else:
            result = num / den

        cosine[(target, context)] = result
    
    return cosine

def output(cosine, singleWordsCounts, coWordCount, pmiMatrix, PMI_INDEX):

    #print(cosine)
    for target, context in cosine:
        
        word1 = target
        word2 = context
        try:
            word1Count = singleWordsCounts[word1]
        except:
            word1Count = 0
        
        try:
            word2Count = singleWordsCounts[word2]
        except:
            word2Count = 0
        try:
            coWCount = coWordCount[word1][word2]
        except:
            coWCount = 0

        if word1 not in PMI_INDEX or word2 not in PMI_INDEX:
            pmi = '0' 
        else:
            pmi = pmiMatrix[PMI_INDEX[word1]][PMI_INDEX[word2]]

        print("{:.5f} {} {} {} {} {} {:.5f}".format(float(cosine[(word1,word2)]), word1, word2, word1Count, word2Count, coWCount, float(pmi)), sep="\t")

def main(filepath, windowSize, wordPairsFile):
    """
    Our main driver for the program.
    """
    
    data = preProcessing(filepath)  # Process the data.
    singleWordsCounts = getCount(data)  # Gather the single word counts.

    totalCount = getTotalCount(singleWordsCounts)   # Gather the total word count

    print("Tokens = {:,}, Types = {:,}, Window = {}".format(totalCount, len(data), windowSize))

    wordPairs = getWordPairs(wordPairsFile) # Gather the word pairs from our file

    coWords = bigram(data, windowSize)  # Gather the co-occurance words and create bigrams.

    coWordCount = getCoWordCount(coWords)   # Gather the word counts of each co-occurance word.
    
    pmiMatrix, PMI_INDEX, INVERSE = createMatrix(singleWordsCounts) # Create our PMI matrix

    pmiMatrixTrain = calculatePMI(coWordCount, singleWordsCounts, totalCount, pmiMatrix, PMI_INDEX) # Calc. PMI

    result = computeCosine(pmiMatrix, PMI_INDEX, wordPairs, coWordCount, INVERSE)   # Calc. cosine.

    output(result, singleWordsCounts, coWordCount, pmiMatrix, PMI_INDEX)    # Display the results to the user.

if __name__ == "__main__":
    #print(sys.argv)

    print("PA 4 computing similarity from a word by word PMI co-occurrence matrix, programmed by Joseph Hnatek.")

    windowSize = int(sys.argv[1])
    filepath = sys.argv[2]
    wordPairsFile = sys.argv[3]

    

    main(filepath, windowSize, wordPairsFile)
