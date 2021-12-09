"""backEnd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import view, modelMangement, ensemble, orderManagement, logs, discussionManagement
from django.conf.urls import url

urlpatterns = [
    path('', view.hello),
    path('modelmarket_backend/', view.hello),
    path('modelmarket_backend/login', view.login),
    path('modelmarket_backend/getIdentity', view.getIdentity),
    path('modelmarket_backend/logout', view.logout),
    path('modelmarket_backend/register', view.register),
    path('modelmarket_backend/getUserInfo', view.getUserInfo),
    path('modelmarket_backend/changeUserInfo', view.changeUserInfo),
    path('modelmarket_backend/charge', view.charge),
    path('modelmarket_backend/resetPassword', view.resetPassword),
    path('modelmarket_backend/getUserList', view.getUserList),
    path('modelmarket_backend/changeUserStatus', view.changeUserStatus),
    path('modelmarket_backend/changePassword', view.changePassword),
    path('modelmarket_backend/ensemble_sklearn', ensemble.ensemble_sklearn),
    path('modelmarket_backend/downloadModel', modelMangement.downloadModel),
    path('modelmarket_backend/queryModels', modelMangement.queryModels),
    path('modelmarket_backend/queryModel', modelMangement.queryModel),
    path('modelmarket_backend/uploadModel', modelMangement.uploadModel),
    path('modelmarket_backend/uploadFile', modelMangement.uploadFile),
    path('modelmarket_backend/manageModel', modelMangement.manageModel),
    path('modelmarket_backend/deleteModel', modelMangement.deleteModel),
    path('modelmarket_backend/changeModelStatus', modelMangement.changeModelStatus),
    path('modelmarket_backend/queryModelsManagement', modelMangement.queryModelsManagement),
    path('modelmarket_backend/buyModel', orderManagement.buyModel),
    path('modelmarket_backend/queryPurchasedOrders', orderManagement.queryPurchasedOrders),
    path('modelmarket_backend/querySoldOrders', orderManagement.querySoldOrders),
    path('modelmarket_backend/queryOrder', orderManagement.queryOrder),
    path('modelmarket_backend/queryLog', logs.queryLog),
    path('modelmarket_backend/queryLogs', logs.queryLogs),
    path('modelmarket_backend/queryDiscussions', discussionManagement.queryDiscussions),
    path('modelmarket_backend/queryDiscussion', discussionManagement.queryDiscussion),
    path('modelmarket_backend/addReply', discussionManagement.addReply),
    path('modelmarket_backend/addTopic', discussionManagement.addTopic),
    path('modelmarket_backend/queryNotifications', discussionManagement.queryNotifications),
]
handler404 = view.S04