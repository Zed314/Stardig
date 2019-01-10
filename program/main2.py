
import numpy as np # linear algebra

import heapq
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os
#from csv import reader
import re

def printcsv(data):
    out  = open("sub.csv", "w")
    out.write("RowId,prediction\r\n")
    for i,elt in enumerate(data):
        out.write(str(i+1)+","+elt+"\r\n")
    print("done")
    out.close()

def isAction(strAction):
    if not strAction :
        return False
    return strAction == "s" or strAction == "Base" or strAction.startswith("hotkey")
def isTime(strAction):
    if not strAction:
        return False
    return strAction[0]=="t"
def getTime(strAction):

    return int(strAction[1:])

def getNbOfHotKey(strAction):
    if strAction.startswith("hotkey"):
        return (int(strAction[6]),int(strAction[7]))
    else:
        return (-1,-1)


def analyseExtendedLine(line, isTrain, timeParameterInSec, disableException=False):
    timeParameterInSec = 30
    #data = line.split(',')
    data = re.split(r',(?=")', line)
    if isTrain :
        nbColRace = 1
        startAction = 2
    else:
        nbColRace = 0
        startAction = 1
    if len(data)== startAction and not disableException:
        raise ValueError('Bad')

    dictF = {}

    greetings = False
    speak = False
    greetingshfgggl = False
    thirdSelection = False
    justgg = True
  #  print(data[0])
  #  print(data[startAction])
  #  print(data[startAction+1])
  #  print(data[startAction+2])
    currTimeInFrame = 0 # 16 Frames in one second
    nbOccCameraEvent = 0
    nbSel = 0
    avgSel = 0
    gg = False
    for i in range(startAction,len(data)):
        dataCell = data[i].split(':')
        try:
            currTimeInFrame = int(dataCell[0])
        except ValueError:
            print(data[i-1])
            print(data[i])
            print(data[i+1])
        if len(dataCell)==3:
            if dataCell[1]=="SelectionEvent":
                if i == startAction +2:
                    thirdSelection = True
                if currTimeInFrame < timeParameterInSec*16:
                    selectionElt = dataCell[2].split(";")
                    nbSel +=1
                    avgSel += len(selectionElt)
                    #print(len(selectionElt))
                    #print(dataCell[2])
            if dataCell[1]=="ChatEvent":
                if dataCell[2]=="gl hf~":
                    greetings = True
                    justgg = False
                elif "hfggg" in dataCell[2] :
                    greetingshfgggl = True
                    justgg = False
                elif dataCell[2] == "gg" or dataCell[2].startswith("gg") or dataCell[2] == "GG":
                    gg = True
                else :
                    justgg = False
                speak = True
        
        if currTimeInFrame < timeParameterInSec*16:
            if dataCell[1]=="BasicCommandEvent":
                nbOccCameraEvent +=1
                #print(data[0])
                #print(dataCell[2])
    if nbSel !=0:
        dictF["selNbInAvg"] =int(avgSel/nbSel)
       # print(avgSel/nbSel)
    else:
        dictF["selNbInAvg"]=0
    #dictF["justgg"]=justgg and gg
    dictF["gg"] = gg
    dictF["nbSel"]=nbSel
    dictF["greetings"]=greetings
    dictF["greetingshfgggl"]=greetingshfgggl
    dictF["speak"]=speak
    dictF["thirdSelection"]=thirdSelection
    dictF["occCameraEvent"]=nbOccCameraEvent
    
    #if(greetings):
    #    print(data[0])
    #    print(greetings)
    return dictF.values()

def analyseLine(line, isTrain,timeParameterInSec,disableException=False):
   # timeParameterInSec = 30
  #  if timeParameterInSec == 60:
   #     print("aaaa")
    data = line.split(',')
    if isTrain :
        nbColRace = 1
        startAction = 2
    else:
        nbColRace = 0
        startAction = 1
    
    if len(data)== startAction and not disableException:
        raise ValueError('Bad')
    
    dictF = {'Zerg': data[nbColRace]=="Zerg","Terran": data[nbColRace]=="Terran"}


    #timerWithoutHK = 0
    nbActionInFirstSecs = 0
    for i in range(startAction,len(data)):
        if data[i].startswith("t"):
            currTime = getTime(data[i])
            if currTime >= timeParameterInSec:
                break
        else:
            nbActionInFirstSecs += 1
    dictF["actionsAtFirst"] = nbActionInFirstSecs
    howMuchHKDefBeforeActionRes = False
    howMuchHKDefBeforeAction = 0
    singleMin = False
    tabHotKeyUsage = [0] * 10
    tabHotKeyCreation = [0] * 10
    tabHotKeyUsed = [0] * 10
    tabHotKeyUpdate = [0] * 10

    nthHKDefined = [-1] * 10
    nbHKDefined = 0
    for i in range(startAction,len(data)):
        if isTime(data[i]):
            currTime = getTime(data[i])
            #timerWithoutHK += 5
            if currTime > timeParameterInSec:
               break
            continue
        nbHK = getNbOfHotKey(data[i])
        if (nbHK[0] != -1):
                tabHotKeyUsage[nbHK[0]] += 1
                if nbHK[1] ==0:
                    tabHotKeyCreation[nbHK[0]] +=1
                elif nbHK[1] ==1:
                    tabHotKeyUsed[nbHK[0]] +=1
                elif nbHK[1] ==2:
                    tabHotKeyUpdate[nbHK[0]] +=1

                if nbHK[1] != 0 and howMuchHKDefBeforeActionRes == False:
                    howMuchHKDefBeforeActionRes = True
                elif nbHK[1] == 0 :
                    if howMuchHKDefBeforeActionRes == False:
                        howMuchHKDefBeforeAction +=1
                    if nbHKDefined < 10:
                        nthHKDefined[nbHKDefined] = nbHK[0]
                        nbHKDefined +=1
             #   timerWithoutHK = 0
        elif data[i] == "SingleMineral":
            singleMin = True

    for i in range(10):
        dictF["usage"+str(i)] = tabHotKeyUsage[i]
        dictF["creation"+str(i)] = tabHotKeyCreation[i]
        dictF["update"+str(i)] = tabHotKeyUpdate[i]
        dictF["used"+str(i)] = tabHotKeyUsed[i]

    
    for i,HKdefined in enumerate(nthHKDefined):
        dictF["HKdefined"+str(i)] = HKdefined
    dictF["hkDefBefAct"]=howMuchHKDefBeforeAction
    dictF["singleMin"]=singleMin
   # print(timerWithoutHK)
  # dictF["timerWithoutHK"] = timerWithoutHK>=10
    if isTrain:
        #add the name
       # print(data[0])
       # print(dictF)
        return dictF.values(), data[0]
    return dictF.values()


def getTestPath():
    return  "/home/zvergne/Documents/5IF/FouillesDeDonnees/Stardig/input/test.csv/TEST.CSV"

def getTrainPath():
    return  "/home/zvergne/Documents/5IF/FouillesDeDonnees/Stardig/input/train.csv/TRAIN.CSV"
def getExtendedTrainPath():
    return  "/home/zvergne/Documents/5IF/FouillesDeDonnees/Stardig/input/train_long.csv/TRAIN_LONG.CSV"
def getExtendedTestPath():
    return  "/home/zvergne/Documents/5IF/FouillesDeDonnees/Stardig/input/test_long.csv/TEST_LONG.CSV"


def trainAndTagTest(timeParameter):
    analysedLines,playerNames = addFeatures(True,timeParameter)
    #print(len(playerNames))
    #playerNames=detectAndReplaceDoubleAccount(playerNames)
    #print(len(playerNames))
    clf = RandomForestClassifier(n_estimators=100).fit(analysedLines, playerNames)


    analysedLines = addFeatures(False,timeParameter)
    return clf.predict(analysedLines)

def addFeatures(isTrain,timeParameter):
    if isTrain:
        path = getTrainPath()
        pathExtended = getExtendedTrainPath()
    else:
        path = getTestPath()
        pathExtended = getExtendedTestPath()
    with open(path) as file:
        with open(pathExtended) as fileExtended:
            analysedLines = []
            playerNames = []
            
            for line in file:
                lineExtended = fileExtended.readline()
                
                if isTrain:
                    try:
                        analysedLine,playerName = analyseLine(line,True,timeParameter, False)
                              
                    except ValueError:
                        print("Error was avoided")
                        continue
                else:
                    analysedLine = analyseLine(line,False,timeParameter,True)
                features = []
                for feature in analysedLine:
                    features.append(feature)
                
                if isTrain:
                    try:
                        analysedLine = analyseExtendedLine(lineExtended,True,timeParameter,False)
                    except ValueError:
                        print("Error was avoided in analyseExtendedLine")
                        continue
                else:
                    analysedLine = analyseExtendedLine(lineExtended,True,timeParameter,False)
                #print(analysedLine)
                for feature in analysedLine:
                    features.append(feature)
                # print(features)
                analysedLines.append(features)
                if isTrain:
                    playerNames.append(playerName)

        
    if isTrain:
        #add the name
        return analysedLines, playerNames
    return analysedLines
def getAllPlayOfAPlayer(name):
    print(name)
    with open(getTrainPath()) as file:
        with open(getExtendedTrainPath()) as fileExtended:
            for line in file:
                if line.startswith(name):
                    print(line[0:200])
            for line in fileExtended:
                if line.startswith(name):
                    print(line[0:200])
                    a = line.split(",")
                    for w in a:
                        sub = w.split(":")
                        if len(sub) ==3:
                            if sub[1].startswith("ChatEvent"):
                                print(w)



def detectAndReplaceDoubleAccount(playerNames):
    dictOccurencies = {}
    done = {}
    for playerName in playerNames:
        dictOccurencies[playerName] = dictOccurencies.get(playerName, 0) + 1
    homonymeBank = {}
    synonymBank = {}
    for playerName in playerNames:
        splittedPlayerName = playerName.split("/")
        username = splittedPlayerName[len(splittedPlayerName)-2]
        if not( username in homonymeBank):
            homonymeBank[username] = [playerName]
        elif not (playerName in homonymeBank[username]):
            homonymeBank[username].append(playerName)


    for homonymes in homonymeBank.values():
        if len(homonymes) <= 1:
            continue
        max = 0
        playerNameMax = ""
        for homonyme in homonymes:
            if dictOccurencies[homonyme] > max :
                max = dictOccurencies[homonyme]
                playerNameMax = homonyme
        for homonyme in homonymes:
            if homonyme != playerNameMax:
                playerNames[:] = [x if x !=homonyme  else playerNameMax for x in playerNames]


    dictOccurencies = {}
    usernameToPlayername  = {}
    for playerName in playerNames:
        splittedPlayerName = playerName.split("/")
        username = splittedPlayerName[len(splittedPlayerName)-2]
        dictOccurencies[username] = dictOccurencies.get(username, 0) + 1
        usernameToPlayername[username]=playerName
    # on dit deux synonymes max
    for playerName in playerNames:
        splittedPlayerName = playerName.split("/")
        username = splittedPlayerName[len(splittedPlayerName)-2]
        if not (username in synonymBank):
            found = False
            for usernameB in synonymBank.keys():
                if username == usernameB:
                    continue
                if username in usernameB :
                    #on inverse
#                    print("AAA")
 #                   print(username)
  #                  print(usernameB)
                    synonymBank[username] = synonymBank.pop(usernameB)
                    synonymBank[username].append(usernameB)
                   # filter(lambda a: a != username, synonymBank[username])
                    found = True
                elif usernameB in username: #and username !=usernameB:
                    if username not in synonymBank[usernameB]:
                        synonymBank[usernameB].append(username)
                    found = True
            
            if not found:
                synonymBank[username]=[]
   # print(synonymBank)
    nbReplaced = 0
    #print(playerNames)
    for synonym in synonymBank.keys():
        if len(synonymBank[synonym])==0:
            continue
        max = dictOccurencies[synonym]
        synMax = synonym
     #   print(synonym)
      #  print(synonymBank[synonym])
        for synToReplace in synonymBank[synonym]:
                if dictOccurencies[synToReplace] > max :
                    max = dictOccurencies[synToReplace]
                    synMax = synToReplace
        #print("Synmax")
       # print(synMax)
        nbReplaced +=1


        synonymBank[synonym].append(synonym)
        for synToReplace in synonymBank[synonym]:
            if synToReplace != synMax:
                playerNames[:] = [x if x !=usernameToPlayername[synToReplace] else usernameToPlayername[synMax] for x in playerNames]
  #  print(nbReplaced)
 #   print(playerNames)
    return playerNames

    for playerName in playerNames:



        for playerNameB in playerNames:
            if playerName == playerNameB :#or done.get(playerName,False)or done.get(playerNameB,False):
                continue
            splittedPlayerName = playerName.split("/")
            username = splittedPlayerName[len(splittedPlayerName)-2]
            splittedPlayerName = playerNameB.split("/")
            usernameB = splittedPlayerName[len(splittedPlayerName)-2]
            
            if username == usernameB:
                print("Match")
                print(playerName)
                print(playerNameB)
                if dictOccurencies[playerName]>dictOccurencies[playerNameB]:
                    for i,playerNameToReplace in enumerate(playerNames):
                        if playerNameToReplace == playerNameB:
                            playerNames[i] = playerName
                else :
                    for i,playerNameToReplace in enumerate(playerNames):
                        if playerNameToReplace == playerName:
                            playerNames[i] = playerNameB
                done[playerName] = True
                done[playerNameB] = True
    return playerNames

def trainAndEvaluateOnTrainData(timeParameter):
    analysedLines, playerNames= addFeatures(True,timeParameter)

    #playerNames=detectAndReplaceDoubleAccount(playerNames)
  #  print(analysedLines)
  #  print(playerNames)
    X_train, X_test, y_train, y_test = train_test_split(analysedLines, playerNames)
   # print(y_train)
   
    y_train_real=y_train.copy()
  #  y_train=detectAndReplaceDoubleAccount(y_train)
   
   
   # print(y_train)
   # print("AEUEAE")
   # print(len(analysedLines))
   # print(len(X_train))
    clf = RandomForestClassifier(n_estimators=100).fit(X_train, y_train)
    print('Accuracy of Decision Tree classifier on test set: {:.4f}'.format(clf.score(X_test, y_test)))
    print('Accuracy of Decision Tree classifier on train set: {:.4f}'.format(clf.score(X_train, y_train_real)))

    res = clf.predict(X_test)
    diff = (res!=y_test)
    for i,elt in enumerate(X_test):
        if diff[i]:
            continue
            print("Elt:")
            print(elt)
            print("Predicted : ")
            print(res[i])
            getAllPlayOfAPlayer(res[i])
            print("Real :")
            print(y_test[i])
            getAllPlayOfAPlayer(y_test[i])
            input("Press the <ENTER> key to continue...")
    #print(X_test[(res!=y_test)])
def putIdOnTest(trainData,testData, doAnEstimation=False):

    #features = []
   # training = trainData
    training = trainData.apply(lambda row: pd.Series(dictFeatures(row)), axis=1)
    training_answer = trainData["IDplayer"]

    clf = RandomForestClassifier(n_estimators=100).fit(training, training_answer)

    X_train, X_test, y_train, y_test = train_test_split(training, training_answer, random_state=0)
    print('Accuracy of Decision Tree classifier on training set: {:.4f}'.format(clf.score(X_train, y_train)))
    print('Accuracy of Decision Tree classifier on all set: {:.4f}'.format(clf.score(training, training_answer)))
    for i,elt in enumerate(clf.predict(training)):
        if(training_answer[i]!=elt):
            print("Error")
            print(elt)
            print(training_answer[i])
            print("Play:")
            print(trainData.iloc[[2]])
            print("All the play of the player")
            print(trainData.loc[trainData['IDplayer'] == elt])
            print("All the play of the answer")
            print(trainData.loc[trainData['IDplayer'] == training_answer[i]])
    print('Accuracy of Decision Tree classifier on test set: {:.4f}'.format(clf.score(X_test, y_test)))
    test = testData.apply(lambda row: pd.Series(dictFeatures(row)), axis=1)

    #print(test)
    return clf.predict(test)

def readFile(name):
   # filepath = "../input/"+name.lower()+".csv/"+name.upper()+".CSV"
    filepath = "/home/zvergne/Documents/5IF/FouillesDeDonnees/Stardig/input/"+name.lower()+".csv/"+name.upper()+".CSV"
    maxNbColumn = -1
    nbLines
    with open(filepath) as fp:
        line = fp.readline()
        while line:
            length = len(line.split(","))
            if (length> maxNbColumn):
                maxNbColumn =length
            line = fp.readline()

def dispPlayplayer(data):
    #print(data.IDplayer.unique())
    for player in data.IDplayer.unique():
        print("Player"+player)
        print(data.loc[data['IDplayer'] == player])

        if player == "http://us.battle.net/sc2/en/profile/4408675/1/TheStC/":
            data.loc[data['IDplayer'] == player].to_csv("player")
            #file = open("player","w")
        #    file.write(str(data.loc[data['IDplayer'] == player]))

#for time in [100,120,130,140,150,160]:
#    print(time)
#    trainAndEvaluateOnTrainData(time)
printcsv(trainAndTagTest(160))
#printcsv(putIdOnTest(readFile("train"),readFile("test")))
