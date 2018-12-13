# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import heapq
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split



# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os
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
    return strAction == "s" or strAction == "Base" or strAction.startswith("hotkey") or strAction.startswith("t")
def isTime(strAction):
    if not strAction:
        return False
    return strAction[0]=="t"
def getTime(strAction):
    strAction.pop(0)
    return int(strAction)

def getNbOfHotKey(strAction):
    if strAction.startswith("hotkey"):
        return (int(strAction[6]),int(strAction[7]))
    else:
        return (-1,-1)

def dictFeatures(row):
    dictF = {'Zerg': row['Race']=="Zerg","Terran": row["Race"]=="Terran"}
    nbActionIn5FirstSec = 0
    singleMin = False
    for action in row:
        if action == "SingleMineral":
            singleMin = True
        if not isAction(action):
            continue
        if action.startswith("t"):
            break
        nbActionIn5FirstSec += 1
    dictF["SingleMineralIn5FirstSec"] =  singleMin
    dictF["nbActionsIn5FirstSec"] = nbActionIn5FirstSec
    favHotKey = 1
    tabHotKeyUsage = [0] * 10
    firstHK = -1
    secondHK = -1
    thirdHK = -1
    fourthHK = -1
    HKspressed = [-1] * 4
    timeHKpressed = [-1] * 4
    howMuchHKDefBeforeAction = 0
    howMuchHKDefBeforeActionRes = -1
    currTime = 0
    for action in row:
        if isAction(action):
            nbHK = getNbOfHotKey(action)

            if (nbHK[0] != -1):
                tabHotKeyUsage[nbHK[0]] += 1
                if nbHK[1] != 0 and howMuchHKDefBeforeActionRes == -1:
                    howMuchHKDefBeforeActionRes = howMuchHKDefBeforeAction
                else:
                    howMuchHKDefBeforeAction +=1
                for i in range(4):
                    if HKspressed[i]==-1 and (i>0 and nbHK[0]!=HKspressed[i-1]):
                        HKspressed[i]= nbHK[0]
                        timeHKpressed[i] = currTime
        elif isTime(action):
            currTime = getTime(action)


    for i,key in enumerate(HKspressed):
        dictF[str(i)+"HK"] = key
        dictF[str(i)+"HKtime"] = timeHKpressed[i]
#    print(tabHotKeyUsage)

    dictF["howMuchHKDefBeforeAction"] = howMuchHKDefBeforeActionRes
#    print("Row")
#    print(firstHK)
#    print(secondHK)
#    print(thirdHK)



    for i in [0,9,8,7,6]:
        dictF["useHK"+str(i)+"MoreThan 10 times"] = tabHotKeyUsage[i] >10
        dictF["useHK"+str(i)] = tabHotKeyUsage[i] >0
    dictF["favHK"] = tabHotKeyUsage.index(max(tabHotKeyUsage))
    nlargest = heapq.nlargest(2, tabHotKeyUsage)
    dictF["secfavHK"] = tabHotKeyUsage.index(nlargest[1])
    tabHotKeyUsage = [0] * 10
    for action in row:
        if isAction(action):
            nbHK = getNbOfHotKey(action)
            if (nbHK[0] != -1):
                tabHotKeyUsage[nbHK[0]] += 1
        elif isTime(action):
            currTime = getTime(action)
            if currTime > 100:
                break

    for i,key in enumerate(tabHotKeyUsage):
        dictF[str(i)+"proportionInBegin"] = key

    return dictF

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
    test = "test" in name
    with open(filepath) as fp:
        line = fp.readline()
        while line:
            length = len(line.split(","))
            if (length> maxNbColumn):
                maxNbColumn =length
            line = fp.readline()

    if("test" in name):
        columns = ["Race"] + list(range(0, maxNbColumn-1))
    else:
        columns = ["IDplayer", "Race"] + list(range(0, maxNbColumn-2))

    return  pd.read_csv(filepath, names=columns, engine='python')

def dispPlayplayer(data):
    #print(data.IDplayer.unique())
    for player in data.IDplayer.unique():
        print("Player"+player)
        print(data.loc[data['IDplayer'] == player])

        if player == "http://us.battle.net/sc2/en/profile/4408675/1/TheStC/":
            data.loc[data['IDplayer'] == player].to_csv("player")
            #file = open("player","w")
        #    file.write(str(data.loc[data['IDplayer'] == player]))


#todo : first used
#todo : how many definition before first use
#todo : order of definition
#todo : timeframe of definition of each hk (or just for the 5 first)
#dispPlayplayer(readFile("train"))
printcsv(putIdOnTest(readFile("train"),readFile("test")))
#putIdOnTest(readFile("train"),readFile("test"))

# Any results you write to the current directory are saved as output.
