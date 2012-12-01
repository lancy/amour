from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf
from weibo import APIClient
from operator import itemgetter
import bayesian

APP_KEY = "3049348926"
APP_SECRET = "712a1724b4d5e38b3a1895d6efce205d"
CALLBACK_URL = "http://127.0.0.1:8000/amour"


def index(request):
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    requestResults = dict()

    if "code" in request.GET:
        print("in request code, set_cookie")
        code = request.GET['code']
        r = client.request_access_token(code)
        access_token = r.access_token
        expires_in = r.expires_in
        client.set_access_token(access_token, expires_in)
    elif "access_token" in request.COOKIES:
        print("has access_token in cookies")
        access_token = request.COOKIES["access_token"]
        expires_in = request.COOKIES["expires_in"]
        client.set_access_token(access_token, expires_in)

    if not client.is_expires():
        print("client is not expires, get information")
        accountUid = client.get.account__get_uid()
        usersShow = client.get.users__show(uid=accountUid["uid"])
        requestResults["usersShow"] = usersShow
    else:
        print("client is expire, authorize again")
        authorizeUrl = client.get_authorize_url()
        requestResults["authorizeUrl"] = authorizeUrl

    response = render_to_response("amour/index.html", requestResults)

    if client.is_expires():
        print("client is expires, clear cookie")
        response.delete_cookie("access_token")
        response.delete_cookie("expires_in")
    else:
        print("client is not expires, set cooke")
        response.set_cookie("access_token", access_token)
        response.set_cookie('expires_in', expires_in)
    return response


def training(request):
    requestResults = dict()
    requestResults.update(csrf(request))


    if "train1" in request.POST:
        hitList = list()
        misList = list()
        counter = 1
        trainLabel = "train%d" % counter
        while trainLabel in request.POST:
            if request.POST[trainLabel] == "pass":
                pass
            elif request.POST[trainLabel] == "hit":
                text = request.POST["text%d" % counter]
                hitList.append(text)
            elif request.POST[trainLabel] == "mis":
                text = request.POST["text%d" % counter]
                misList.append(text)

            counter = counter + 1
            trainLabel = "train%d" % counter

        bayesian.appendListToDefaultHitFileWithList(hitList)
        bayesian.appendListToDefaultMisFileWithList(misList)
        requestResults["message"] = "Training Completed"
        print "Training Completed"

    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    access_token = request.COOKIES["access_token"]
    expires_in = request.COOKIES["expires_in"]
    client.set_access_token(access_token, expires_in)

    publicTimeline = client.get.statuses__public_timeline(count=20)
    statusesList = list()
    probabilityTable = bayesian.defaultTokensProbabilityTable()

    for dictionary in publicTimeline["statuses"]:
        state = dict()
        state["text"] = dictionary["text"]
        state["probability"] = bayesian.eventProbabilityFromStringAndTokensProbabilityTable(state["text"], probabilityTable)
        statusesList.append(state)

    statusesList.sort(key=itemgetter("probability"), reverse=True)

    requestResults["statusesList"] = statusesList
    response = render_to_response("amour/training.html", requestResults)
    return response


def single(request):
    probabilityTable = bayesian.defaultTokensProbabilityTable()
    requestResults = dict()
    requestResults.update(csrf(request))
    if "string" in request.POST:
        testString = request.POST["string"].strip()
        probability = bayesian.eventProbabilityFromStringAndTokensProbabilityTable(testString, probabilityTable)
        requestResults["text"] = testString
        requestResults["probability"] = probability
    elif "train" in request.POST:
        text = request.POST["text"]
        train = request.POST["train"]
        tempList = [text]
        if train == "hit":
            bayesian.appendListToDefaultHitFileWithList(tempList)
        elif train == "mis":
            bayesian.appendListToDefaultMisFileWithList(tempList)
        requestResults["message"] = "Training Completed"

    response = render_to_response("amour/single.html", requestResults)
    return response


