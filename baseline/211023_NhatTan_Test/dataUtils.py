import os
from copy import deepcopy
import pandas as pd
import numpy as np

from constants import *


def readData(path):
    with open(path, 'r', encoding = 'utf8') as file:
        allLine = file.readlines()
    return allLine


def writeData(allLine, fileName):

    with open(fileName, 'w', encoding = 'utf8') as file:
        for line in allLine:
            file.write(line)
    pass


def dropDoubleDuplicates(allLine1, allLine2, verbose = True):

    assert len(allLine1) == len(allLine2)

    combineDF = pd.DataFrame({
        'text1': allLine1,
        'text2': allLine2,
    })

    combineDFNoDoubleDuplicates = combineDF.drop_duplicates()

    if (verbose):
        print('Dropped %d samples out of %d. Leftover: %d' %
              (len(combineDF) - len(combineDFNoDoubleDuplicates), len(combineDF), len(combineDFNoDoubleDuplicates)))

    return (combineDFNoDoubleDuplicates['text1'].to_list(),
            combineDFNoDoubleDuplicates['text2'].to_list())


def getLineLen(allLine, mode):
    lineLen = []
    countEmptyLine = 0

    for line in allLine:

        lineStripped = line.strip()

        if len(lineStripped) == 0:
            countEmptyLine += 1

        if (mode == 'word'):
            lineLen.append(len(lineStripped.split(' ')))
        elif (mode == 'character'):
            lineLen.append(len(lineStripped))
        else:
            print('WARNING: INVALID MODE!')

    return lineLen, countEmptyLine


def lenRatioThresholding(allLine1, allLine2, mode, lowerThreshold, upperThreshold, verbose = True):
    """
    :param allLine1: Should be Vi
    :param allLine2: Should be Lo
    :return:
    """

    assert len(allLine1) == len(allLine2)
    assert lowerThreshold <= upperThreshold

    len1, _ = getLineLen(allLine1, mode = mode)
    len2, _ = getLineLen(allLine2, mode = mode)

    len1NP = np.array(len1)
    len2NP = np.array(len2)
    lenRatio = len1NP / len2NP

    combineDF = pd.DataFrame({
        'text1': allLine1,
        'text2': allLine2,
        'lenRatio': lenRatio.tolist(),
    })

    combineDFThresholded = combineDF[(combineDF['lenRatio'] >= lowerThreshold)
                                     & (combineDF['lenRatio'] <= upperThreshold)]

    if (verbose):
        print('Dropped %d samples out of %d. Leftover: %d' %
              (len(combineDF) - len(combineDFThresholded), len(combineDF), len(combineDFThresholded)))

    return (combineDFThresholded['text1'].to_list(),
            combineDFThresholded['text2'].to_list())


def countEmojiInLine(allLine, ALL_EMOJI = ALL_EMOJI):

    countList = []

    for line in allLine:
        countDictLine = dict()
        for emo in ALL_EMOJI:
            countEmo = line.count(emo)
            if (countEmo != 0):
                countDictLine[emo] = countEmo
        countList.append(deepcopy(countDictLine))

    return countList


def cleanEmoji(allLine1, allLine2, verbose = True):

    countList1 = countEmojiInLine(allLine1)
    countList2 = countEmojiInLine(allLine2)

    assert len(allLine1) == len(allLine2)
    assert len(allLine1) == len(countList1)
    assert len(allLine2) == len(countList2)

    allLine1Cleaned = []
    allLine2Cleaned = []
    willAppend = None
    noClear = 0

    for i in range(len(allLine1)):

        text1 = allLine1[i]
        text2 = allLine2[i]

        if (len(countList1[i]) == 0):
            allLine1Cleaned.append(text1)
            allLine2Cleaned.append(text2)

        elif ((len(countList1[i]) == len(countList2[i]))
              & (len(countList1[i]) != 0)
              & (set(countList1[i].keys()) == set(countList2[i].keys()))):

            willAppend = True
            for emo in set(countList1[i].keys()):
                if (countList1[i][emo] == countList2[i][emo]):
                    text1 = text1.replace(emo, '')
                    text2 = text2.replace(emo, '')
                else:
                    willAppend = False
                    break

            if (willAppend):
                noClear += 1
                allLine1Cleaned.append(text1)
                allLine2Cleaned.append(text2)

    if (verbose):
        print('Cleared %d. Dropped %d out of %d. Leftover: %d' %
              (noClear, len(allLine1) - len(allLine1Cleaned), len(allLine1), len(allLine1Cleaned)))

    return (allLine1Cleaned, allLine2Cleaned)







# TODO: SIGNIFICANT LANGUAGE CHECK (NO METHOD????)
# TODO: LAOS & VIETNAMESE LETTERS/ALPHABET
# TODO: CHECK IRRELEVANT/STRANGE SYMBOLS
# TODO: URL REMOVAL
# TODO: PUNCTUATIONS ANALYSIS
# use import re and string.punctuations



