from django.shortcuts import render_to_response
from weibo import APIClient


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
        print("client is not expires, get infomation")
        accountUid = client.get.account__get_uid()
        usersShow = client.get.users__show(uid=accountUid["uid"])
        userTimeline = client.get.statuses__user_timeline(count=20)
        for statuse in userTimeline["statuses"]:
            statuse["comments"] = client.get.comments__show(id=statuse.id)
        requestResults = {
            "usersShow": usersShow,
            "userTimeline": userTimeline,
        }
        print userTimeline

    else:
        authorizeUrl = client.get_authorize_url()
        requestResults = {
            "authorizeUrl": authorizeUrl
        }
    response = render_to_response("amour/index.html", requestResults)
    if not client.is_expires():
        print("client is not expires, set cookie")
        response.set_cookie("access_token", access_token)
        response.set_cookie("expires_in", expires_in)

    return response


# def results(request):
#     code = request.GET['code']
#     client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
#     r = client.request_access_token(code)
#     access_token = r.access_token
#     expires_in = r.expires_in
#     client.set_access_token(access_token, expires_in)
#     accountUid = client.get.account__get_uid()
#     usersShow = client.get.users__show(uid=accountUid["uid"])
#     userTimeline = client.get.statuses__user_timeline(count=100)
#     requestResults = {
#         "userTimeline": userTimeline,
#         "usersShow": usersShow,
#     }
#     response = render_to_response("amour/results.html", requestResults)
#     response.set_cookie("access_token", access_token)
#     response.set_cookie("expires_in", expires_in)
#     return response
