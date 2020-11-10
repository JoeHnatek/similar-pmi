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
        #print(filename)
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
        #result = fiveGram(data)
        pass
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
    #print(dim)
    
    pmiMatrix = numpy.zeros((dim, dim), int) # target (row) x context (col)

    PMI_INDEX = {}
    INVERSE = {}
    index = 0

    for word in data:
        PMI_INDEX[word] = index
        INVERSE[index] = word
        index += 1

    #print(PMI_INDEX)
    
    #pmiMatrix[PMI_INDEX["the"]][PMI_INDEX["dog"]] = 5

    #print(pmiMatrix)

    return pmiMatrix, PMI_INDEX, INVERSE

def calculatePMI(data, singleWordsCounts, totalCount, pmiMatrix, PMI_INDEX):

    for target in singleWordsCounts:
        for context in singleWordsCounts:
            if target in data and context in data[target]:
                if context in data[target]:

                    p = data[target][context] / (data[target][context])

                    p1 = singleWordsCounts[target] / totalCount
                    p2 = singleWordsCounts[context] / totalCount

                    #if PMI_INDEX[target] > 9999 or PMI_INDEX[context] > 9999:
                     #   break
                    pmiMatrix[PMI_INDEX[target]][PMI_INDEX[context]] = math.log2(p/(p1*p2))

    return pmiMatrix


def computeCosine(pmiMatrix, PMI_INDEX, wordPairs, coWordCount, INVERSE):
    
    cosine = {}
    print(coWordCount)
    for pair in wordPairs:

        target = pair[0]
        context = pair[1]

        if target not in PMI_INDEX or context not in PMI_INDEX:
            cosine[tuple(pair)] = -999
            continue

        """if PMI_INDEX[target] > 10000 or PMI_INDEX[context] > 10000:
            cosine[tuple(pair)] = 69
            continue"""
        
        targetIndexRow = PMI_INDEX[target]
        contextIndexRow = PMI_INDEX[context]

        countNum = 0
        countTargetDen = 0
        countContextDen = 0

        for i in range(len(pmiMatrix)):
            targetRowValue = pmiMatrix[targetIndexRow][i]
            contextRowValue = pmiMatrix[contextIndexRow][i]
            
            countNum += targetRowValue * contextRowValue

            temp1 = INVERSE[targetIndexRow]
            #print(INVERSE)
            temp2 = INVERSE[i]
            temp3 = INVERSE[contextIndexRow]
            #print("temp2: ", temp2)

            if temp1 not in coWordCount or temp2 not in coWordCount[temp1]:
                val1 = 0
            else:
                val1 = coWordCount[temp1][temp2]

            if temp3 not in coWordCount or temp2 not in coWordCount[temp3]:
                val3 = 0
            else:
                val3 = coWordCount[temp3][temp2]
            
            countTargetDen += val1**2
            
            countContextDen += val3**2

            #print(countContextDen)

        #print(countTargetDen, countContextDen)
        pairCosineValue = countNum / (math.sqrt(countTargetDen) * math.sqrt(countContextDen))

        cosine[tuple(pair)] = pairCosineValue

    print(cosine)



def main(filepath, windowSize, wordPairsFile):
    
    data = preProcessing(filepath)
    singleWordsCounts = getCount(data)

    totalCount = getTotalCount(singleWordsCounts)

    wordPairs = getWordPairs(wordPairsFile)

    coWords = findCoWords(data, windowSize)

    coWordCount = getCoWordCount(coWords)
    pmiMatrix, PMI_INDEX, INVERSE = createMatrix(singleWordsCounts)

    pmiMatrixTrain = calculatePMI(coWordCount, singleWordsCounts, totalCount, pmiMatrix, PMI_INDEX)

    #print(pmiMatrix[PMI_INDEX["clinton"]][PMI_INDEX["clinton"]])

    computeCosine(pmiMatrix, PMI_INDEX, wordPairs, coWordCount, INVERSE)

    #print(PMI_INDEX["clinton"])


if __name__ == "__main__":
    #print(sys.argv)

    windowSize = int(sys.argv[1])
    filepath = sys.argv[2]
    wordPairsFile = sys.argv[3]

    

    main(filepath, windowSize, wordPairsFile)