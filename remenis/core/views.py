from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
import datetime, random, re, logging
from remenis.core.models import User, Story, TaggedUser, BetaEmail
from remenis import settings

from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

import urllib, urllib2, json
from operator import itemgetter
from itertools import groupby

@csrf_exempt
def splash(request):
    if request.method == 'POST':
        try:
            existing_email = BetaEmail.objects.get(email=request.POST["email"])
        except BetaEmail.DoesNotExist:
            email_to_save = BetaEmail(email=request.POST["email"],
                                      submit_date=datetime.datetime.now()
                                      )
            email_to_save.save()
        return render_to_response('thankyou.html', locals())
    else:
        return render_to_response('splash.html', locals())
    
@csrf_exempt
def login(request):
    debug = settings.DEBUG
    if 'token' in request.session:
        return redirect('/home/')
    else:
        return render_to_response('login.html', locals())

def logout(request):
    request.session.pop('token', None)
    request.session.pop('profile', None)
    request.session.pop('accessCredentials', None)
    return redirect('/login/')

@csrf_exempt
def home(request):
    if 'token' in request.session:
        fullname = getMyFullName(request)
        userid = (request.session['accessCredentials']).get('uid')
        photourl = (request.session['profile']).get('photo')
    elif 'token' in request.POST and request.POST['token']:
        request.session['token'] = request.POST['token']
        
        auth_info = getAuthInfo(request)
        if auth_info <> False:
            profile = auth_info['profile']
            request.session['profile'] = profile
            
            fullname = profile.get('displayName')
            photourl = profile.get('photo')
            email = profile.get('verifiedEmail')
            name = profile['name']
            firstname = name.get('givenName')
            lastname = name.get('familyName')
            
            request.session['accessCredentials'] = auth_info['accessCredentials']
            
            userid = (request.session['accessCredentials']).get('uid')
            
            try:
                user = User.objects.get(fbid=userid)
            except User.DoesNotExist:
                # save new user to user DB
                user_to_save = User(fbid=userid,
                                    first_name=firstname,
                                    last_name=lastname,
                                    full_name=fullname,
                                    email=email,
                                    is_registered=True
                                    )
                user_to_save.save()
            else:
                if user.is_registered == False: # user has already been tagged in a story, but this is their first time logging into Remenis
                    user.fbid = userid
                    user.first_name = firstname
                    user.last_name = lastname
                    user.full_name = fullname
                    user.email = email
                    user.is_registered = True
                    user.save()                    
        else:
            return redirect('/login/')
    else:
        return redirect('/login/')
    
    fullname = getMyFullName(request)
    userid = (request.session['accessCredentials']).get('uid')
    
    myfriends = getGraphForMe(request, 'friends', True)
    
    friends_name_array = [x['name'].encode('ASCII', 'ignore') for x in myfriends]
    friends_name_array.append(str(fullname))
    friends_name_array_temp = [str.replace(name, "'", "&#39;") if "'" in name else name for name in friends_name_array]
    friends_name_array_string =  str.replace(str(friends_name_array_temp), "'", "\"")
    
    friends_id_array = [x['id'].encode('ASCII', 'ignore') for x in myfriends]
    friends_id_array.append(str(userid))
    
    friends_dictionary = json.dumps(dict(zip(friends_id_array, friends_name_array)))

    if 'q' in request.GET:
        if request.GET['q']:
            query = request.GET['q']
            return redirect('/' + query)
        else:
            return redirect('/searcherror/?error=1')
        
    active_tab = "home"
    return render_to_response('home.html', locals())

@csrf_exempt
def profile(request, profileid=""):
    if not 'token' in request.session:
        return redirect('/login/')
    
    fullname = getMyFullName(request)
    userid = (request.session['accessCredentials']).get('uid')
    
    myfriends = getGraphForMe(request, 'friends', True)
    
    friends_name_array = [x['name'].encode('ASCII', 'ignore') for x in myfriends]
    friends_name_array.append(str(fullname))
    friends_name_array_temp = [str.replace(name, "'", "&#39;") if "'" in name else name for name in friends_name_array]
    friends_name_array_string =  str.replace(str(friends_name_array_temp), "'", "\"")
    
    friends_id_array = [x['id'].encode('ASCII', 'ignore') for x in myfriends]
    friends_id_array.append(str(userid))
    
    friends_dictionary = json.dumps(dict(zip(friends_id_array, friends_name_array)))

    if 'q' in request.GET:
        active_tab = "none"
        if request.GET['q']:
            query = request.GET['q']
            return redirect('/' + query)
        else:
            return redirect('/searcherror/?error=1')
    elif profileid == "":
        profileid = userid
    elif not profileid in friends_id_array:
        not_friend = True
        profile_name = getUserFullName(profileid)
        return render_to_response('profile.html', locals())    
    
    if profileid == userid:
        active_tab = "profile"
    
    try:    
        user = User.objects.get(fbid=profileid)
    except User.DoesNotExist:
        stories_written_by_user = []
        profile_name = getUserFullName(profileid)
    else:    
        stories_written_by_user = Story.objects.filter(authorid = user)
        profile_name = user.full_name
    
    stories_about_user = [x.storyid for x in TaggedUser.objects.filter(fbid = profileid)]
    for story_written_by_user in stories_written_by_user:
        if not story_written_by_user in stories_about_user:
            stories_about_user.append(story_written_by_user)
    stories_about_user = sorted(stories_about_user, key=lambda x: x.post_date, reverse=True) # sort by post date
    stories_about_user_ids = [x.id for x in stories_about_user]
    tagged_users = []
    for story in stories_about_user:
        tagged_user_objects_in_story = TaggedUser.objects.filter(storyid = story)
        tagged_users_in_story = []
        for tagged_user_object_in_story in tagged_user_objects_in_story:
            try:
                tagged_user = User.objects.get(fbid=tagged_user_object_in_story.fbid)
            except User.DoesNotExist:
                tagged_users_in_story.append(User(fbid=tagged_user_object_in_story.fbid,
                                    full_name="",
                                    is_registered=False
                                    ))
            else:
                tagged_users_in_story.append(tagged_user)
        tagged_users.append(tagged_users_in_story)
    stories_dictionary = dict(zip(stories_about_user_ids, tagged_users))
    
    return render_to_response('profile.html', locals())

@csrf_exempt
def searcherror(request):
    if not 'token' in request.session:
        return redirect('/login/')
    
    fullname = getMyFullName(request)
    userid = (request.session['accessCredentials']).get('uid')
    
    myfriends = getGraphForMe(request, 'friends', True)
    
    friends_name_array = [x['name'].encode('ASCII', 'ignore') for x in myfriends]
    friends_name_array.append(str(fullname))
    friends_name_array_temp = [str.replace(name, "'", "&#39;") if "'" in name else name for name in friends_name_array]
    friends_name_array_string =  str.replace(str(friends_name_array_temp), "'", "\"")
    
    friends_id_array = [x['id'].encode('ASCII', 'ignore') for x in myfriends]
    friends_id_array.append(str(userid))
    
    friends_dictionary = json.dumps(dict(zip(friends_id_array, friends_name_array)))

    if 'q' in request.GET:
        if request.GET['q']:
            query = request.GET['q']
            return redirect('/' + query)
        else:
            return redirect('/searcherror/?error=1')

    if 'error' in request.GET and request.GET['error']:
        error = getErrorMessage(request.GET['error'])
    return render_to_response('search_form.html', locals())

@csrf_exempt
def post(request): 
    if not 'token' in request.session:
        return redirect('/login/')
    
    active_tab = "post"
    
    fullname = getMyFullName(request)
    userid = (request.session['accessCredentials']).get('uid')
    
    myfriends = getGraphForMe(request, 'friends', True)
    
    friends_name_array = [x['name'].encode('ASCII', 'ignore') for x in myfriends]
    friends_name_array.append(str(fullname))
    friends_name_array_temp = [str.replace(name, "'", "&#39;") if "'" in name else name for name in friends_name_array]
    friends_name_array_string =  str.replace(str(friends_name_array_temp), "'", "\"")
    
    friends_id_array = [x['id'].encode('ASCII', 'ignore') for x in myfriends]
    friends_id_array.append(str(userid))
    
    friends_dictionary_temp = dict(zip(friends_id_array, friends_name_array))
    friends_dictionary = json.dumps(friends_dictionary_temp)
    
### HANDLE DUPLICATE NAMES 
#    import collections
#    friends_name_array_counter = collections.Counter(friends_name_array)
#    friends_name_array_duplicate = [i for i in y if y[i] > 1]
#    for duplicate_name in friends_name_array_duplicate:
#        for name in friends_name_array:
    
    if request.method == 'GET':
        return redirect('/home/')
    elif request.method == 'POST':
        user = User.objects.get(fbid=(request.session['accessCredentials']).get('uid'))
        
        date_month_int = 0
        if 'story_date_month' in request.POST:
            date_month_string = request.POST["story_date_month"]
            if date_month_string == "Jan":
                date_month_int = 1
            elif date_month_string == "Feb":
                date_month_int = 2
            elif date_month_string == "Mar":
                date_month_int = 3
            elif date_month_string == "Apr":
                date_month_int = 4
            elif date_month_string == "May":
                date_month_int = 5
            elif date_month_string == "Jun":
                date_month_int = 6
            elif date_month_string == "Jul":
                date_month_int = 7
            elif date_month_string == "Aug":
                date_month_int = 8
            elif date_month_string == "Sep":
                date_month_int = 9
            elif date_month_string == "Oct":
                date_month_int = 10
            elif date_month_string == "Nov":
                date_month_int = 11
            elif date_month_string == "Dec":
                date_month_int = 12
            
        date_day_int = 0
        if 'story_date_day' in request.POST:
            if request.POST["story_date_day"] != "---":
                date_day_int = request.POST["story_date_day"]
            
        story_to_save = Story(authorid=user,
                      title=request.POST["title"],
                      story=request.POST["story"],
                      story_date_year=request.POST["story_date_year"],
                      story_date_month=date_month_int,
                      story_date_day=date_day_int,
                      post_date=datetime.datetime.now()
                       )
        
        tagged_friends = (request.POST["tagged_friends"]).split(",")
        
        story_to_save.save()
        
        for tagged_friend in tagged_friends:
            taggedUser_to_save = TaggedUser(fbid=tagged_friend,
                                            storyid=story_to_save
                                            )
            taggedUser_to_save.save()
            try:    
                user = User.objects.get(fbid=tagged_friend)
            except User.DoesNotExist:
                user_to_save = User(fbid=tagged_friend,
                                    full_name=friends_dictionary_temp[tagged_friend],
                                    is_registered=False
                                    )
                user_to_save.save()

        return redirect('/' + user.fbid)


## UTILS
    
def getErrorMessage(errorid):
    if errorid == '1':
        return 'Please submit a valid search term.'
    if errorid == '2':
        return 'User has not registered for Remenis.  Would you like to invite?'
    if errorid == '3':
        return 'User is not your Facebook friend.'

def getAuthInfo(request):
    api_params = {
        'token': request.session['token'],
        'apiKey': '7d0e7d31faa15fcd3e88e41908ae63c2d37cc5a5',
        'format': 'json',
    }
    # make the api call
    http_response = urllib2.urlopen('https://rpxnow.com/api/v2/auth_info', urllib.urlencode(api_params))
    
    # read the json response
    auth_info_json = http_response.read()
    
    # process the json response
    auth_info = json.loads(auth_info_json)

    if auth_info['stat'] == 'ok':
        return auth_info
    else:
        return False

def getGraphData(request, url_to_open):
    http_response = urllib2.urlopen(url_to_open)
    graph_json = http_response.read()
    graph = json.loads(graph_json)
    return graph['data']

def getGraphForMe(request, graph_string, access_token_needed=False):
    url_to_open = 'https://graph.facebook.com/' + (request.session['accessCredentials']).get('uid') + '/' + graph_string
    if access_token_needed:
        url_to_open += '?access_token=' + (request.session['accessCredentials']).get('accessToken')
    return getGraphData(request, url_to_open)

def getGraphCustom(request, graph_string, access_token_needed=False):
    url_to_open = 'https://graph.facebook.com/' + graph_string
    if access_token_needed:
        url_to_open += '?access_token=' + (request.session['accessCredentials']).get('accessToken')
    return getGraphData(request, url_to_open)

def getUserFullName(fbid):
    url_to_open = 'https://graph.facebook.com/' + fbid
    http_response = urllib2.urlopen(url_to_open)
    graph_json = http_response.read()
    graph = json.loads(graph_json)
    if not graph == False:
        return graph['name']
    else:
        return ""
    
def getMyFullName(request):
    user = User.objects.get(fbid=(request.session['accessCredentials']).get('uid'))
    return user.full_name
