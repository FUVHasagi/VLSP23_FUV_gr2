from utilFuncs.constants import *


def generateSplitInd(datasetSize, p1, p2, p3, NP_SEED = NP_SEED):

    assert (np.around(p1 + p2 + p3) == 1)

    ind = list(range(datasetSize))
    splitInd = int(np.floor(p1 * datasetSize))
    splitInd2 = int(np.ceil(p2 * datasetSize))

    np.random.seed(NP_SEED)
    np.random.shuffle(ind)

    (splitSet1Ind, splitSet2Ind, splitSet3Ind) = (ind[: splitInd],
                                                ind[splitInd: splitInd + splitInd2],
                                                ind[splitInd + splitInd2:])

    return (splitSet1Ind, splitSet2Ind, splitSet3Ind)


def splitDataset(allLine1, allLine2, p1, p2, p3):

    assert len(allLine1) == len(allLine2)

    (splitSet1Ind, splitSet2Ind, splitSet3Ind) = generateSplitInd(len(allLine1), p1, p2, p3)

    splitFunc1 = operator.itemgetter(*splitSet1Ind)
    splitFunc2 = operator.itemgetter(*splitSet2Ind)
    if (len(splitSet3Ind) == 0):
        splitFunc3 = lambda x : []

    return (
        (list(splitFunc1(allLine1)), list(splitFunc1(allLine2))),
        (list(splitFunc2(allLine1)), list(splitFunc2(allLine2))),
        (list(splitFunc3(allLine1)), list(splitFunc3(allLine2))),
    )


def findFiles(files, relative_path, verbose = True):
    pathsToFiles = []
    for file in files:
        pathsToFiles += glob.glob("%s/%s" % (relative_path, file), recursive = True)

    if (verbose):
        print('Found %d paths' % (len(pathsToFiles)))

    return pathsToFiles

def readData(path):
    # pathLst = glob.glob(path)

    with open(path, 'r', encoding = 'utf8') as file:
        allLine = file.readlines()
    return allLine


def readAllData(paths, verbose = True):
    allData = []
    for path in paths:
        allData.append(readData(path))

    if (verbose):
        print('Read %d files' % (len(allData)))

    return allData

def writeData(allLine, fileName):

    with open(fileName, 'w', encoding = 'utf8') as file:
        for line in allLine:
            file.write(line)
    pass


def createDataset(allVi, allLo):
    allViConcat = []
    for dataVi in allVi:
        allViConcat += dataVi

    allLoConcat = []
    for dataLo in allLo:
        allLoConcat += dataLo

    assert (len(allLoConcat) != 0) | (len(allViConcat) != 0)

    if (len(allLoConcat) == 0):
        return Dataset.from_dict({
            'translation': Dataset.from_dict({
                'vi': allViConcat,
            })
        })
    elif (len(allViConcat) == 0):
        return Dataset.from_dict({
            'translation': Dataset.from_dict({
                'lo': allLoConcat,
            })
        })
    else:
        return Dataset.from_dict({
            'translation': Dataset.from_dict({
                'lo': allLoConcat,
                'vi': allViConcat,
            })
        })


def fixHTMLSpecialCharacter(allLine, verbose = True):
    """
    Fix space within HTML special entities, numbers, names
    :param allLine:
    :param verbose:
    :return:
    """
    allLineFixed = []
    countFixed = 0

    for line in allLine:
        tempLine = deepcopy(line)
        tempLine = (tempLine.replace("& ", "&")
                    .replace("# ", '#')
                    .replace("< ", '<'))
        allLineFixed.append(deepcopy(tempLine))
        if (tempLine != line):
            countFixed += 1

    assert len(allLine) == len(allLineFixed)

    if (verbose):
        print('Fixed %d' % (countFixed))

    return allLineFixed


def cleanHTMLFormat(allLine, verbose = True):
    """
    Get text out of HTML if the sentence contains HTML syntax. Else the same sentence will be returned.
    :param allLine:
    :param verbose:
    :return:
    """

    allLineCleaned = []
    countCleaned = 0

    allLineFixed = fixHTMLSpecialCharacter(allLine)

    for line in allLineFixed:
        tempLine = deepcopy(line)
        tempLine = BeautifulSoup(tempLine, "html.parser").get_text()
        allLineCleaned.append(deepcopy(tempLine))
        if (tempLine != line):
            countCleaned += 1

    assert len(allLine) == len(allLineCleaned)

    if (verbose):
        print('Cleared %d' % (countCleaned))

    return allLineCleaned


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


def rmPunctuation(allLine, punctuationList = string.punctuation):

    allLineCleaned = []

    for line in allLine:
        allLineCleaned.append(deepcopy(line.strip("\n").translate(str.maketrans('', '', punctuationList))) + "\n")

    assert len(allLineCleaned) == len(allLine)

    return allLineCleaned


def rmSpace(allLine):

    allLineCleaned = []

    for line in allLine:
        allLineCleaned.append(deepcopy(line.replace(" ", "")))

    assert len(allLine) == len(allLineCleaned)

    return allLineCleaned


def getLineLen(allLine, mode, removePunctuation, removeSpace = False):

    assert (mode == 'sentence') | (mode == 'character')

    lineLen = []
    countEmptyLine = 0

    if (removePunctuation):
        allLine = rmPunctuation(allLine)

    if (removeSpace):
        allLine = rmSpace(allLine)

    for line in allLine:

        lineStripped = line.strip("\n")

        if len(lineStripped) == 0:
            countEmptyLine += 1

        if (mode == 'word'):
            lineLen.append(len(list(filter(None, lineStripped.split(' ')))))

        elif (mode == 'character'):
            lineLen.append(len(lineStripped))

    assert len(lineLen) == len(allLine)

    return lineLen, countEmptyLine


def lenThresholding(allLine1, allLine2, mode, removePunctuation, lowerThreshold, upperThreshold, removeSpace = False,
                    verbose = True):
    """
    Length thresholding with respect to the first iterable object (allLine1). ORDER MATTER!
    :param allLine1:
    :param allLine2:
    :param mode:
    :param removePunctuation:
    :param lowerThreshold:
    :param upperThreshold:
    :param removeSpace: default: False
    :param verbose:
    :return:
    """
    assert len(allLine1) == len(allLine2)
    assert lowerThreshold <= upperThreshold

    len1, _ = getLineLen(allLine1, mode = mode, removePunctuation = removePunctuation, removeSpace = removeSpace)

    len1NP = np.array(len1)

    combineDF = pd.DataFrame({
        'text1': allLine1,
        'text2': allLine2,
        'len1': len1NP.tolist(),
    })

    combineDFThresholded = combineDF[(combineDF['len1'] >= lowerThreshold)
                                     & (combineDF['len1'] <= upperThreshold)]

    if (verbose):
        print('Dropped %d samples out of %d. Leftover: %d' %
              (len(combineDF) - len(combineDFThresholded), len(combineDF), len(combineDFThresholded)))

    return (combineDFThresholded['text1'].to_list(),
            combineDFThresholded['text2'].to_list())


def lenRatioThresholding(allLine1, allLine2, mode,
                         removePunctuation1, removePunctuation2,
                         lowerThreshold, upperThreshold,
                         removeSpace1 = False, removeSpace2 = False, verbose = True):
    """

    :param allLine1: should be Vi
    :param allLine2: should be Lo
    :param mode:
    :param removePunctuation1:
    :param removePunctuation2:
    :param removeSpace1:
    :param removeSpace2:
    :param lowerThreshold:
    :param upperThreshold:
    :param verbose:
    :return:
    """

    assert len(allLine1) == len(allLine2)
    assert lowerThreshold <= upperThreshold

    len1, _ = getLineLen(allLine1, mode = mode, removePunctuation = removePunctuation1, removeSpace = removeSpace1)
    len2, _ = getLineLen(allLine2, mode = mode, removePunctuation = removePunctuation2, removeSpace = removeSpace2)

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
    countClear = 0

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
                countClear += 1
                allLine1Cleaned.append(text1)
                allLine2Cleaned.append(text2)

    if (verbose):
        print('Cleared %d. Dropped %d out of %d. Leftover: %d' %
              (countClear, len(allLine1) - len(allLine1Cleaned), len(allLine1), len(allLine1Cleaned)))

    return (allLine1Cleaned, allLine2Cleaned)


def cleanSpecialSpacing(allLine1, allLine2, removeMode, SPECIAL_SPACING = SPECIAL_SPACING, verbose = True):
    """
    NBSP and ZWSP handling
    :param allLine1:
    :param allLine2:
    :param removeMode:
    :param verbose:
    :return:
    """

    assert (removeMode == 'sentence') | (removeMode == 'special_spacing')
    assert len(allLine1) == len(allLine2)

    allLine1Cleaned = []
    allLine2Cleaned = []
    countClear = 0

    if (removeMode == 'sentence'):
        for line1, line2 in zip(allLine1, allLine2):
            willAppend = True
            for specialSpace in SPECIAL_SPACING:
                if ((specialSpace in line1) | (specialSpace in line2)):
                    willAppend = False
                    break
            if (willAppend):
                allLine1Cleaned.append(deepcopy(line1))
                allLine2Cleaned.append(deepcopy(line2))
    elif (removeMode == 'special_spacing'):
        for line1, line2 in zip(allLine1, allLine2):
            tempLine1, tempLine2 = deepcopy(line1), deepcopy(line2)
            for specialSpace in SPECIAL_SPACING:
                tempLine1 = tempLine1.replace(specialSpace, '')
                tempLine2 = tempLine2.replace(specialSpace, '')
            if ((line1 != tempLine1) | (line2 != tempLine2)):
                countClear += 1
            allLine1Cleaned.append(deepcopy(tempLine1))
            allLine2Cleaned.append(deepcopy(tempLine2))


    if (verbose):
        print('Cleared %d. Dropped %d out of %d. Leftover: %d' %
              (countClear, len(allLine1) - len(allLine1Cleaned), len(allLine1), len(allLine1Cleaned)))

    return (allLine1Cleaned, allLine2Cleaned)


def adjustQuoting(allLine, verbose = True):

    allLineCleaned = []
    countClear = 0

    for line in allLine:
        tempLine = deepcopy(line)
        tempLine = tempLine.replace("''", '"').replace("``", '"')
        allLineCleaned.append(deepcopy(tempLine))
        if (tempLine != line):
            countClear += 1

    assert len(allLine) == len(allLineCleaned)

    if (verbose):
        print('Cleared %d' % (countClear))

    return allLineCleaned


def cleanFontError(allLine1, allLine2, FONT_ERRORS = FONT_ERRORS, verbose = True):

    assert len(allLine1) == len(allLine2)

    allLine1Cleaned, allLine2Cleaned = [], []

    for line1, line2 in zip(allLine1, allLine2):
        willAppend = True
        for fontErr in FONT_ERRORS:
            if ((fontErr in line1) | (fontErr in line2)):
                willAppend = False
                break
        if (willAppend):
            allLine1Cleaned.append(deepcopy(line1))
            allLine2Cleaned.append(deepcopy(line2))

    if (verbose):
        print('Dropped %d out of %d. Leftover: %d' %
              (len(allLine1) - len(allLine1Cleaned), len(allLine1), len(allLine1Cleaned)))

    return (allLine1Cleaned, allLine2Cleaned)


def viAlphaNumericThresholding(allLine1, allLine2, threshold, VI_ALL = VI_ALL, verbose = True):
    """
    Vi Alpha-Numeric thresholding
    :param allLine1: should be Vi
    :param allLine2: should be Lo
    :param threshold:
    :param verbose:
    :return:
    """
    assert len(allLine1) == len(allLine2)

    allLine1Cleaned, allLine2Cleaned = [], []

    for (line1, line2) in zip(allLine1, allLine2):

        tempLine1 = deepcopy(line1)
        tempLine1 = tempLine1.replace(' ', '')
        count = 0

        for char in tempLine1:
            if char in VI_ALL:
                count += 1

        ratio = count / len(tempLine1)
        if (ratio > threshold):
            allLine1Cleaned.append(line1)
            allLine2Cleaned.append(line2)

    assert len(allLine1) == len(allLine2)

    if (verbose):
        print('Dropped %d out of %d. Leftover: %d' %
              (len(allLine1) - len(allLine1Cleaned), len(allLine1), len(allLine1Cleaned)))

    return (allLine1Cleaned, allLine2Cleaned)


def loCharacterNumericThresholding():  # TODO
    pass


def rmNewLineCharacter(allLine):
    return list(map(str.strip, allLine))


def countOccurrence(allLine, query, mode):

    assert query is not None
    assert (mode == 'sentence') | (mode == 'occurrence')

    totalCount = 0

    for line in allLine:
        countLine = line.count(query)
        if (countLine != 0):
            if (mode == 'sentence'):
                totalCount += 1
            elif (mode == 'occurrence'):
                totalCount += countLine

    return totalCount







# FINISHED: HTML SPECIAL CHARACTERS ADJUST - HUMAN-OBSERVATIONS
# FINISHED: HTML ENTITIES (&QUOT) - BEAUTIFUL SOUP 4
# FINISHED: DOUBLE DUPLICATE - PANDAS DF
# FINISHED: LENGTH RATIO THRESHOLDING - NUMPY
# FINISHED: EMOJIS - EMOJI + HUMAN-OBSERVATIONS
# FINISHED: SPECIAL SPACING (ZWSP + NBSP) - LOOPS
# FINISHED: DOUBLE QUOTES (OPEN - CLOSE) - PATTERN-MATCHING
# FINISHED: FONTS ERROR - LOOPS

# TODO: SIGNIFICANT LANGUAGE CHECK - (NO METHOD????) - LARGE LANGUAGE DICT?
# TODO: LAOS & VIETNAMESE LETTERS/ALPHABET - USE 'HAND-LABEL'?
# TODO: CHECK IRRELEVANT/STRANGE SYMBOLS - REGEX?
# TODO: CURRENCY
# TODO: COMPARISON SYMBOL
# TODO: URL REMOVAL HTTPS/HTTP - MAYBE REGEX CAN HELP (IN FACT, TRY USING HTML BS4 FIRST)
# TODO: EMAIL
# TODO: COPYRIGHT/SAVE AT/<START - DUR>/THẺ: CÁ CƯỢC/... FORMS REMOVE - (COSINE SIMILARITY?) - TRY HTML BS4
# TODO: PUNCTUATIONS ANALYSIS - MAYBE REGEX CAN HELP

# NOTES: HTML DOES NOT CARE ABOUT SPACING, ONLY NEED ;
# USE: import re and string.punctuations (FOR REGEX AND PUNCTUATIONS_LIST)





