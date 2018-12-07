# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split



# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os

def readFile(name):
    filepath = "../input/"+name.lower()+".csv/"+name.upper()+".CSV"
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
        columns = ["Race"] + list(range(0, maxNbColumn-2))
    else:
        columns = ["IDplayer", "Race"] + list(range(0, maxNbColumn-2))

    res = pd.read_csv(filepath, names=columns, engine='python')

    features = []
    #group by player
    if not test:
        playerToPlay = dict()
        print(res["IDplayer"])
        for id in res["IDplayer"]:
            print(id)
            if not (id in playerToPlay):
                playerToPlay[id] = res.loc[res['IDplayer'] == id]
        #for id in playerToPlay.keys():
        #    playerToPlay[id] = res.loc[res['IDplayer'] == id]
      #  for id in playerToPlay:
       #     print(id)
        #    print(playerToPlay[id]["Race"])
         #   print(playerToPlay[id][0])
       # print(playerToPlay)
    print(res["IDplayer"].unique())
    print(res.groupby('IDplayer').size())
    question = res[["Race",0,1,2]]
    question = pd.get_dummies(question,prefix=['race', "first","second","third"], drop_first=True)

   # question.loc[question['Race'] == 'Protoss', 'Race'] = 1
#    question.loc[question['Race'] == 'Terran', 'Race'] = 2
 #   question.loc[question['Race'] == 'Zerg', 'Race'] = 4
    answer = res["IDplayer"]
    X_train, X_test, y_train, y_test = train_test_split(question, answer, random_state=0)
    clf = DecisionTreeClassifier().fit(X_train, y_train)

    print('Accuracy of Decision Tree classifier on training set: {:.2f}'
     .format(clf.score(X_train, y_train)))
    print('Accuracy of Decision Tree classifier on test set: {:.2f}'
     .format(clf.score(X_test, y_test)))

    


readFile("train")
# Any results you write to the current directory are saved as output.