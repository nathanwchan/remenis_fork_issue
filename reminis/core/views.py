#from django.template.loader import get_template
#from django.template import Context
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
import datetime, random, re, logging
from reminis.core.models import User, Story, TaggedUser
from reminis import settings

from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from django_facebook import exceptions as facebook_exceptions, settings as facebook_settings
from django_facebook.api import get_persistent_graph, get_facebook_graph, FacebookUserConverter, require_persistent_graph
from django_facebook.canvas import generate_oauth_url
from django_facebook.connect import CONNECT_ACTIONS, connect_user
from django_facebook.utils import next_redirect, get_registration_backend, get_oauth_url
from django_facebook.decorators import (facebook_required,
                                        facebook_required_lazy)
from open_facebook.utils import send_warning
from open_facebook.exceptions import OpenFacebookException

import urllib, urllib2, json

@csrf_exempt
def splash(request):
    return render_to_response('splash.html', locals())
    
@csrf_exempt
def login(request):
#    context = RequestContext(request)
#    graph = get_facebook_graph(request)
#    try:
#        facebook = FacebookUserConverter(graph).is_authenticated()
#        if facebook:
#            fb = require_persistent_graph(request)
#            name = fb.get('me')['name']
#            return render_to_response('home.html', locals())
#    except:
#        authenticated = False
#    else:
#        authenticated = True
#    return render_to_response('login.html', locals())
    debug = settings.DEBUG
    if 'token' in request.session:
        return redirect('/home/')
    else:
        return render_to_response('login.html', locals())

def logout(request):
    request.session.pop('token', None)
    request.session.pop('profile', None)
    request.session.pop('accessCredentials', None)
    return redirect('/')

@csrf_exempt
def home(request):
    active_tab = "home"

    if 'token' in request.session:
        fullname = loadUsername(request)
        userid = (request.session['accessCredentials']).get('uid')
        photourl = (request.session['profile']).get('photo')
        return render_to_response('home.html', locals())
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
            
#            identifier = profile.get('identifier')
#            userid = re.search(r'id=(\d+)', identifier).group(1)
            userid = (request.session['accessCredentials']).get('uid')
            
            try:
                user = User.objects.get(fbid=userid)
            except User.DoesNotExist:
                # save new user to user DB
                user_to_save = User(fbid=userid,
                                    first_name=firstname,
                                    last_name=lastname,
                                    full_name=fullname,
                                    email=email
                                    )
                user_to_save.save()
            
            return render_to_response('home.html', locals())
        else:
            return redirect('/')
    else:
        return redirect('/')
                
#    if 'profile' in request.POST:
#        if request.POST['profile']:
#            profilename = request.POST['profile'].displayname
#    context = RequestContext(request)
#    graph = get_facebook_graph(request)
#    try:
#        facebook = FacebookUserConverter(graph)
#        facebook.is_authenticated()
#        user = _connect_user(request, facebook, overwrite=False)
#        accesstoken = user.get_profile().access_token
#    except:
#        authenticated = False
#    else:
#        authenticated = True
#        fb = require_persistent_graph(request)
#        name = fb.get('me')['name']
#    return render_to_response('home.html', locals())

@csrf_exempt
#@facebook_required_lazy(canvas=True)
def post(request): 
    errors = []
    debug = settings.DEBUG
    active_tab = "post"
    
#    fb = require_persistent_graph(request)
#    authorid = fb.get('me')['id']
#    authorname = fb.get('me')['name']
    fullname = loadUsername(request)
    userid = (request.session['accessCredentials']).get('uid')

    story_date = datetime.datetime.now().strftime("%m/%d/%Y")
    
    if request.method == 'GET':
        return render_to_response('post.html', 
                                      locals(),
                                      RequestContext(request)
                                      )
    elif request.method == 'POST':
#        if 'authorid' in request.POST:
#            if not request.POST.get('authorid', ''):
#                errors.append('You must have an authorid.')
#            else:
#                try:
#                    user = User.objects.get(fbid=request.POST["authorid"])
#                except User.DoesNotExist:
#                    errors.append('A user with that authorid doesn\'t exist.')
#        else:
        user = User.objects.get(fbid=(request.session['accessCredentials']).get('uid'))
        
#        if not request.POST.get('story', ''):
#            errors.append('You must submit a story!')
#        if not errors:
        
        if 'story_date_month' in request.POST:
            date_month_string = request.POST["story_date_month"]
            date_month_int = 0
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
        else:
            date_month_int = 0
            
        if 'story_date_day' in request.POST:
            date_day_int = request.POST["story_date_day"]
        else:
            date_day_int = 0
            
        story_to_save = Story(authorid=user,
                      title=request.POST["title"],
                      story=request.POST["story"],
#                      story_date=datetime.datetime.strptime(request.POST["story_date"], '%m/%d/%Y'),
                      story_date_year=request.POST["story_date_year"],
                      story_date_month=date_month_int,
                      story_date_day=date_day_int,
                      post_date=datetime.datetime.now()
                       )
        story_to_save.save()
        
        active_tab = "search"
        return redirect('/search/?q=' + user.fbid)
        
#            return render_to_response('post.html',
#                                      locals(),
#                                      RequestContext(request)
#                                      )
                
#    return render_to_response('post.html', {
#                              'errors': errors,
#                              'active_tab': active_tab,
#                              'fullname': fullname,
#                              'authorid': request.POST.get('authorid', ''),
#                              'title': request.POST.get('title', ''),
#                              'story': request.POST.get('story', ''),
#                              'story_date': request.POST.get('story_date', ''),
#                              },
#                              RequestContext(request)
#                              )

@csrf_exempt
def search(request):
    active_tab = "search"
    
    fullname = loadUsername(request)
    userid = (request.session['accessCredentials']).get('uid')
    
    myfriends = getGraphForMe(request, 'friends', True)
    tagarray = [x['name'].encode('ASCII', 'ignore') for x in myfriends]
    tagarray_temp = [str.replace(tag, "'", "&#39;") if "'" in tag else tag for tag in tagarray]
    tagarray_string =  str.replace(str(tagarray_temp), "'", "\"")
    
    if 'q' in request.GET:
        if request.GET['q']:
            query = request.GET['q']
            try:
                user = User.objects.get(fbid=query)
            except User.DoesNotExist:
                error = 'A user with that authorid doesn\'t exist in Remenis.'
            else:
                stories = Story.objects.filter(authorid = user)
                search_authorname = user.full_name
#                (getGraphCustom(request, 'name'))['name']
#                except Exception:
#                    error = 'User does not exist in Facebook.'
            
            return render_to_response('search_results.html', locals())
        else:
            error = 'Please submit a search term.'
            return render_to_response('search_form.html', locals())
    else:
        return render_to_response('search_form.html', locals())


## UTILS

def getAuthInfo(request):
    api_params = {
        'token': request.session['token'],
        'apiKey': '5ab3ff51bb1b219c07e950e4d8b4dc1ad94496ad',
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
    
def loadUsername(request):
    user = User.objects.get(fbid=(request.session['accessCredentials']).get('uid'))
    return user.full_name
