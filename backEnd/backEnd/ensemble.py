# -*- coding: utf-8 -*-

from .dbconfig import *
from django.http import HttpResponse
import json
from bson import json_util
from .view import check_login, check_parameters, json_wrap
from .modelMangement import downloadModel
from sklearn import datasets
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
import joblib, os
import pickle
import warnings
from django.http import FileResponse
from .dbconfig import *


@check_login
@check_parameters(["models"])
def ensemble_sklearn(request):
    model_ids = request.GET["models"].split(",")
    model_ids = list(map(int, model_ids))
    res = list(models.find({"id":{"$in":model_ids}}))
    classifiers = []
    length = []
    for model in res:
        filename = model["filename"]
        classifier = joblib.load(os.getcwd() + "/models/" + filename)
        classifiers.append((filename,classifier))
        length.append(1)
    eclf = VotingClassifier(estimators=classifiers, voting='soft', weights=length)
    joblib.dump(eclf, os.getcwd() + '/models/ensemble.model')
    filename = os.getcwd() + '/models/ensemble.model'
    file = open(filename, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=ensemble.model'
    return response
