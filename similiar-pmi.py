import sys
import os
import re
import math
import numpy

def preProcessing(filepath):

    newsList = []
    data = ""

    directory = filepath
    for filename in os.listdir(filepath):
        print(filename)
        if filename.endswith(".txt"):
            with open(filepath + '/' + filename, 'r') as file:
                data = file.read()

                data = data.lower()

                data = re.sub(r'([^A-Za-z0-9\n]+)', r' ', data)
                data = data.split('\n')


                for x in range(len(data)):
                    data[x] = data[x].strip()

                if(data[-1] == " " or data[-1] == ''):
                    del data[-1]
            
                #print("Preproc: {}".format(data))

                for line in data:

                    newsList.append(line.split())
                #print("Preproc: {}".format(data))

                data = ""

    #print("test", newsList)

    return newsList


def getCount(data):

    counts = {}

    for line in data:
        for word in line:
            if word not in counts:
                counts[word] = 1
            else:
                counts[word] += 1

    #print(counts)

    return counts


def getTotalCount(data):

    count = 0

    for key, value in data.items():
        count += value

    return count

def getWordPairs(wordPairsFile):

    wordPairs = []

    with open(wordPairsFile) as file:
        data = file.readlines()

        for line in data:
            line = line.split()
            if len(line) != 0:
                wordPairs.append(line)
            

    return wordPairs


def findCoWords(data, windowSize):

    if windowSize == 2:
        result = bigram(data)
    elif windowSize == 5:
        result = fiveGram(data)
    else:
        print("unknown error")
        exit()

    return result

def bigram(data):

    STEP = 1
    N_GRAM = 2

    newTokens = []
    temp = []

    for line in data:
        for i in range(0, len(line), STEP):
            temp.append(line[i : i + N_GRAM])
            
        newTokens.extend(temp)
        temp = []

    bigrams = []

    for x in range(len(newTokens)):
        if len(newTokens[x]) == 2:
            bigrams.append(newTokens[x])

    #print(bigrams)
    #print(len(bigrams))

    return bigrams

def fiveGram(data):
    pass


def getCoWordCount(data):

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

    dim = len(data)
    print(dim)
    
    pmiMatrix = numpy.zeros((dim, dim), int) # target (row) x context (col)

    PMI_INDEX = {}

    index = 0

    for word in data:
        PMI_INDEX[word] = index
        index += 1

    #print(PMI_INDEX)
    
    #pmiMatrix[PMI_INDEX["the"]][PMI_INDEX["dog"]] = 5

    #print(pmiMatrix)

    return pmiMatrix, PMI_INDEX

def calculatePMI(data, singleWordsCounts, totalCount, pmiMatrix, PMI_INDEX):


    for target in singleWordsCounts:
        for context in singleWordsCounts:
            if target in data and context in data[target]:
                if context in data[target]:

                    p = data[target][context] / (data[target][context])

                    p1 = singleWordsCounts[target] / totalCount
                    p2 = singleWordsCounts[context] / totalCount

                    pmiMatrix[PMI_INDEX[target]][PMI_INDEX[context]] = math.log2(p/(p1*p2))

    return pmiMatrix

def main(filepath, windowSize, wordPairsFile):
    
    data = preProcessing(filepath)
    singleWordsCounts = getCount(data)

    totalCount = getTotalCount(singleWordsCounts)

    wordPairs = getWordPairs(wordPairsFile)

    coWords = findCoWords(data, windowSize)

    coWordCount = getCoWordCount(coWords)

    pmiMatrix, PMI_INDEX = createMatrix(singleWordsCounts)

    pmiMatrix = calculatePMI(coWordCount, singleWordsCounts, totalCount, pmiMatrix, PMI_INDEX)

    print(pmiMatrix)

if __name__ == "__main__":
    print(sys.argv)

    windowSize = int(sys.argv[1])
    filepath = sys.argv[2]
    wordPairsFile = sys.argv[3]

    

    main(filepath, windowSize, wordPairsFile)