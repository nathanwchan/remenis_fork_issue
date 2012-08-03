from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
import datetime, random, re, logging, operator
from datetime import timedelta
from remenis.core.models import User, Story, StoryComment, StoryLike, TaggedUser, BetaEmail
from remenis import settings

from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

import urllib, urllib2, json
from operator import itemgetter
from itertools import groupby
    
@csrf_exempt
def login(request):
    if 'token' in request.session:
        return redirect('/home/')
    else:
        token_url = urllib.quote_plus(settings.SITE_ROOT_URL)
        subsite = "home%2F"
        if 'story' in request.GET:
            if request.GET['story']:
                subsite = "story%2F"
                story_id = request.GET['story'] + "%2F"
                return render_to_response('login_story.html', locals())            
    return render_to_response('login.html', locals())

def logout(request):
    clearSession(request)
    return redirect('/')

@csrf_exempt
def home(request):
    if not saveSessionAndRegisterUser(request):
        return redirect('/')

    fullname = getMyFullName(request)
    userid = (request.session['accessCredentials']).get('uid')
    photourl = (request.session['profile']).get('photo')
    
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
    if not saveSessionAndRegisterUser(request):
        return redirect('/')
    
    fullname = getMyFullName(request)
    userid = (request.session['accessCredentials']).get('uid')
    logged_in_user = User.objects.get(fbid=userid)
    
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
        return render_to_response('profile_recent.html', locals())    
    
    if profileid == userid:
        active_tab = "profile"
    
    try:    
        user = User.objects.get(fbid=profileid)
    except User.DoesNotExist:
        stories_written_by_user = []
        profile_name = getUserFullName(profileid)
        stories_about_user_all = []
    else:    
        stories_written_by_user = Story.objects.filter(authorid = user)
        profile_name = user.full_name
        stories_about_user_all = [x.storyid for x in TaggedUser.objects.filter(taggeduserid=user)]
    
    # aggregate stories written by and about user together, removing duplicates 
    for story_written_by_user in stories_written_by_user:
        if not story_written_by_user in stories_about_user_all:
            stories_about_user_all.append(story_written_by_user)

    # exclude private stories
    if profileid == userid:
        stories_about_user = stories_about_user_all
    else:
        stories_about_user = []
        for story in stories_about_user_all:
            if not story.is_private or userid == story.authorid.fbid or userid in [x.taggeduserid.fbid for x in TaggedUser.objects.filter(storyid = story)]:
                stories_about_user.append(story)
    
    if 'display' in request.GET and request.GET['display'] and request.GET['display'] == "timeline":
        stories_about_user = sorted(stories_about_user, key=operator.attrgetter('story_date_year', 'story_date_month', 'story_date_day'), reverse=True) # sort by story date
        profile_html_page = "profile_timeline.html"
    else: # default or recent
        stories_about_user = sorted(stories_about_user, key=lambda x: x.post_date, reverse=True) # sort by post date
        profile_html_page = "profile_recent.html"
    
    stories_about_user_ids = [x.id for x in stories_about_user]
    tagged_users = []
    story_comments = []
    story_likes = []
    story_post_date = []
    for story in stories_about_user:
        tagged_users_in_story = [x.taggeduserid for x in TaggedUser.objects.filter(storyid = story)]
        tagged_users.append(tagged_users_in_story)
        story_comments_of_story = []
        story_comments_objects_of_story = StoryComment.objects.filter(storyid = story)
        for comment in story_comments_objects_of_story:
            story_comments_of_story.append({'storyid': comment.storyid,
                                            'authorid': comment.authorid,
                                            'comment': comment.comment,
                                            'post_date': comment.post_date,
                                            'post_date_for_display': getStoryPostDate(comment.post_date)
                                            })
        story_comments.append(story_comments_of_story)
        story_likes.append(StoryLike.objects.filter(storyid = story))
        story_post_date.append(getStoryPostDate(story.post_date))
    stories_tagged_users_dictionary = dict(zip(stories_about_user_ids, tagged_users))
    stories_comments_dictionary = dict(zip(stories_about_user_ids, story_comments))
    stories_likes_dictionary = dict(zip(stories_about_user_ids, story_likes))
    stories_post_date_dictionary = dict(zip(stories_about_user_ids, story_post_date))
    
    liked_story_ids = [x.storyid.id for x in StoryLike.objects.filter(authorid = logged_in_user)]
    
    if 'display' in request.GET and request.GET['display']:
        display = request.GET['display']
        if display == "recent":
            return render_to_response('profile_recent.html', locals())
        elif display == "timeline":
            return render_to_response('profile_timeline.html', locals())
    return render_to_response('profile_recent.html', locals())

@csrf_exempt
def searcherror(request):
    if not saveSessionAndRegisterUser(request):
        return redirect('/')
    
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
    if not saveSessionAndRegisterUser(request):
        return redirect('/')
    
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
            date_month_int = convertMonthToInt(date_month_string)

        date_day_int = 0
        if 'story_date_day' in request.POST:
            if request.POST["story_date_day"] != "---":
                date_day_int = request.POST["story_date_day"]
        
        is_private = False
        if 'private' in request.POST:
            if request.POST["private"] == "on":
                is_private = True
        
        storyid_for_edit = request.POST["storyid_for_edit"]       
        story = Story()
        newstory = False
        if request.POST["storyid_for_edit"] != "":
            try:
                story = Story.objects.get(id=int(storyid_for_edit))
            except Story.DoesNotExist:
                newstory = True
            else:
                story.title = request.POST["title"]
                story.story = request.POST["story"]
                story.story_date_year = request.POST["story_date_year"]
                story.story_date_month = date_month_int
                story.story_date_day = date_day_int
                story.post_date = datetime.datetime.now()
                story.is_private = is_private
                story.save()
        else:
            newstory = True
            
        if newstory: 
            story = Story(authorid=user,
                          title=request.POST["title"],
                          story=request.POST["story"],
                          story_date_year=request.POST["story_date_year"],
                          story_date_month=date_month_int,
                          story_date_day=date_day_int,
                          post_date=datetime.datetime.now(),
                          is_private = is_private
                          )
            story.save()

        tagged_friends = request.POST["tagged_friends"]
        if tagged_friends == "":
            tagged_friends = []
        else:
            tagged_friends = tagged_friends.split(",")
        
        if not newstory: # editing story
            existing_tagged_users = [x.taggeduserid.fbid for x in TaggedUser.objects.filter(storyid = story)]
            for existing_tagged_user in existing_tagged_users:
                if not existing_tagged_user in tagged_friends:
                    TaggedUser.objects.filter(storyid = story).filter(taggeduserid=User.objects.get(fbid=existing_tagged_user)).delete()
        
        for tagged_friend in tagged_friends:
            try:    
                tagged_user = User.objects.get(fbid=tagged_friend)
            except User.DoesNotExist:
                tagged_user = User(fbid=tagged_friend,
                                    full_name=friends_dictionary_temp[tagged_friend],
                                    is_registered=False
                                    )
                tagged_user.save()
            
            try:
                tagged_user_temp = TaggedUser.objects.get(storyid=story, taggeduserid=tagged_user)
            except TaggedUser.DoesNotExist:
                tagged_user_to_save = TaggedUser(storyid=story, taggeduserid=tagged_user)
                tagged_user_to_save.save()
        
        if newstory:
            share_clause = "?share=" + str(story.id)
        else:
            share_clause = ""
        redirect_url = request.META["HTTP_REFERER"]
        if redirect_url.find('?') != -1:
            return redirect(re.match(r'(.*)\?.*', redirect_url).group(1) + share_clause + "#" + str(story.id))
        return redirect(redirect_url + share_clause + "#" + str(story.id))

@csrf_exempt
def delete(request):
    if request.method == 'POST':
        if 'storyid_for_delete' in request.POST and request.POST["storyid_for_delete"] != "":
            Story.objects.get(id=int(request.POST["storyid_for_delete"])).delete()
            # note: also deletes all TaggedUsers, StoryComments and StoryLikes of this Story
    redirect_url = request.META["HTTP_REFERER"]
    if redirect_url.find('?') != -1:
        return redirect(re.match(r'(.*)\?.*', redirect_url).group(1))
    return redirect(redirect_url)

@csrf_exempt
def comment(request):
    if request.method == 'POST':
        comment_to_save = StoryComment(storyid=Story.objects.get(id=int(request.POST["storyid"])),
                                       authorid=User.objects.get(fbid=(request.session['accessCredentials']).get('uid')),
                                       comment=request.POST["comment"],
                                       post_date=datetime.datetime.now()
                                       )
        comment_to_save.save()
    
                
    redirect_url = request.META["HTTP_REFERER"]
    if redirect_url.find('?') != -1:
        redirect_url = re.match(r'(.*)\?.*', redirect_url).group(1)        
    if "story" in redirect_url:
        return redirect(redirect_url)
    return redirect(redirect_url + '#' + request.POST["storyid"])
    
@csrf_exempt
def like(request, storyid=""):
    try:
        story = Story.objects.get(id=int(storyid))
    except Story.DoesNotExist:
        return redirect(request.META["HTTP_REFERER"])
    else:
        try:
            like = StoryLike.objects.get(storyid=story,
                                         authorid=User.objects.get(fbid=(request.session['accessCredentials']).get('uid'))
                                         )
        except StoryLike.DoesNotExist:    
            like_to_save = StoryLike(storyid=story,
                                     authorid=User.objects.get(fbid=(request.session['accessCredentials']).get('uid'))
                                     )
            like_to_save.save()
            
    redirect_url = request.META["HTTP_REFERER"]
    if redirect_url.find('?share') != -1:
        redirect_url = re.match(r'(.*)\?.*', redirect_url).group(1)        
    if "story" in redirect_url:
        return redirect(redirect_url)
    return redirect(redirect_url + '#' + storyid)

@csrf_exempt
def story(request, storyid=""):
    if not saveSessionAndRegisterUser(request):
        if not storyid == "":
            return redirect('/?story=' + storyid)
        else:
            return redirect('/')
    
    fullname = getMyFullName(request)
    userid = (request.session['accessCredentials']).get('uid')
    logged_in_user = User.objects.get(fbid=userid)
    
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
        
    try:
        story = Story.objects.get(id=int(storyid))
    except Story.DoesNotExist:
        story = False
        error = "Story doesn't exist."
    else:
        # Check if you have access to this story
        story_tagged_users = [x.taggeduserid for x in TaggedUser.objects.filter(storyid = story)]
        # - check if private story
        if story.is_private and userid != story.authorid.fbid and not userid in [x.fbid for x in story_tagged_users]:
            story = False
            error = "You do not have access to this story."
        else:
            story_comments = []
            story_comments_objects = StoryComment.objects.filter(storyid = story)
            for comment in story_comments_objects:
                story_comments.append({'storyid': comment.storyid,
                                       'authorid': comment.authorid,
                                       'comment': comment.comment,
                                       'post_date': getStoryPostDate(comment.post_date)
                                       })
            story_likes = StoryLike.objects.filter(storyid = story)
            story_post_date = getStoryPostDate(story.post_date)
            liked_story_ids = [x.storyid.id for x in StoryLike.objects.filter(authorid = logged_in_user)]
        # analytics - track story page views
        story.page_views += 1
        story.save()
    return render_to_response('story.html', locals())

@csrf_exempt
def api_story(request, storyid=""):
    if not saveSessionAndRegisterUser(request):
        return HttpResponse(False)
    
    userid = (request.session['accessCredentials']).get('uid')
    
    try:
        story = Story.objects.get(id=int(storyid))
    except Story.DoesNotExist:
        return HttpResponse(False)
    else:
        # Check if you have access to this story
        tagged_users = [int(x.taggeduserid.fbid) for x in TaggedUser.objects.filter(storyid = story)]
        # - check if private story
        if story.is_private and userid != story.authorid.fbid and not userid in tagged_users:
            return HttpResponse(False)
        else:
            # remove post date (can't json serialize post_date)
            story_for_json = {'title': story.title,
                              'story': story.story,
                              'story_date_year': story.story_date_year,
                              'story_date_month': story.story_date_month,
                              'story_date_day': story.story_date_day,
                              'is_private': story.is_private,
                              'tagged_users': json.dumps(tagged_users)
                              }
            return HttpResponse(json.dumps(story_for_json))
    return HttpResponse(False)

def messagesent(request):
    return render_to_response('messagesent.html', locals())

## UTILS

def clearSession(request):
    request.session.pop('token', None)
    request.session.pop('profile', None)
    request.session.pop('accessCredentials', None)
            
def saveSessionAndRegisterUser(request):
    if 'token' in request.session:
        if not 'accessCredentials' in request.session:
            clearSession(request)
            return False # weird case, but hit it once
        userid = (request.session['accessCredentials']).get('uid')
        try:
            user = User.objects.get(fbid=userid)
        except User.DoesNotExist:
            clearSession(request)
            return False # something wrong - clear session
        else:
            user.last_date = datetime.datetime.now()
            user.page_views += 1
            user.save()
        return True # already logged in
    elif 'token' in request.POST and request.POST['token']: # just logged in
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
            return True # login successful
        else:
            return False # something in auth from rpxnow failed
    else:
        return False # weird case

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

monthDictionary = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

def convertMonthToString(month_int):
    if monthDictionary.has_key(month_int):
        return monthDictionary[month_int]
    else:
        return "---"

def convertMonthToInt(month_string):
    for key in monthDictionary:
        if monthDictionary[key] == month_string:
            return key
    return 0

def getStoryPostDate(post_datetime):
    now = datetime.datetime.now()
    timedelta = now - post_datetime
    
    if timedelta.days >= 365:
        return str(post_datetime.day) + " " + convertMonthToString(post_datetime.month) + " " + str(post_datetime.year)[2:]
    elif timedelta.days >= 1:
        return str(post_datetime.day) + " " + convertMonthToString(post_datetime.month)
    elif timedelta.seconds >= 3600: # greater than 1 hour ago
        return str(timedelta.seconds / 3600) + "h"
    elif timedelta.seconds >= 60: # greater than 1 minute ago
        return str(timedelta.seconds / 60) + "m"
    else:
        return str(timedelta.seconds) + "s"