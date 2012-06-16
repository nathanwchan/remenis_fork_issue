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
from django_facebook.utils import next_redirect, get_registration_backend
from django_facebook.decorators import (facebook_required,
                                        facebook_required_lazy)
from open_facebook.utils import send_warning
from open_facebook.exceptions import OpenFacebookException

def xd_receiver(request):
    return render_to_response('xd_receiver.html')

def home(request):
    context = RequestContext(request)
    graph = get_facebook_graph(request)
    try:
        facebook = FacebookUserConverter(graph).is_authenticated()
    except:
        authenticated = False
    else:
        authenticated = True
        fb = require_persistent_graph(request)
        name = fb.get('me')['name']
    setting = settings.SITE_ROOT_URL
    return render_to_response('home.html', locals())

def logout(request):
    return render_to_response('logout.html', locals())

@csrf_exempt
@facebook_required_lazy(canvas=True)
def post(request): 
    errors = []
    
    fb = require_persistent_graph(request)
    authorid = fb.get('me')['id']
    authorname = fb.get('me')['name']
    
    story_date = datetime.datetime.now().strftime("%m/%d/%Y")
    
    if request.method == 'GET':
            return render_to_response('post.html', 
                                      locals(),
                                      RequestContext(request)
                                      )
    elif request.method == 'POST':
        if not request.POST.get('authorid', ''):
            errors.append('You must have an authorid.')
        else:
            try:
                user = User.objects.get(fbid=request.POST["authorid"])
            except User.DoesNotExist:
                errors.append('A user with that authorid doesn\'t exist.')
    
        if not request.POST.get('story', ''):
            errors.append('You must submit a story!')
        if not errors:
            story_to_save = Story(authorid=user,
                          title=request.POST["title"],
                          story=request.POST["story"],
                          story_date=datetime.datetime.strptime(request.POST["story_date"], '%m/%d/%Y') #datetime.datetime.now() - datetime.timedelta(days=365*random.random()))
                           )
            story_to_save.save()

            return redirect('/search/?q=' + authorid)
#            return render_to_response('post.html',
#                                      locals(),
#                                      RequestContext(request)
#                                      )
                
    return render_to_response('post.html', {
                              'errors': errors,
                              'authorid': request.POST.get('authorid', ''),
                              'title': request.POST.get('title', ''),
                              'story': request.POST.get('story', ''),
                              'story_date': request.POST.get('story_date', ''),
                              },
                              RequestContext(request)
                              )

def search(request):
    
    fb = require_persistent_graph(request)
    authorid = fb.get('me')['id']
    authorname = fb.get('me')['name']
    myfriends = fb.get('me/friends')['data']
    tagarray = [x['name'].encode('ASCII', 'ignore') for x in myfriends]
    
    if 'q' in request.GET:
        if request.GET['q']:
            query = request.GET['q']
            try:
                user = User.objects.get(fbid=query)
            except User.DoesNotExist:
                error = 'A user with that authorid doesn\'t exist.'
            else:
                stories = Story.objects.filter(authorid = user)
                try:
                    search_authorname = fb.get(query)['name']
                except Exception:
                    error = 'User does not exist in Facebook.'
            
            return render_to_response('search_results.html', locals())
        else:
            error = 'Please submit a search term.'
            return render_to_response('search_form.html', locals())
    else:
        return render_to_response('search_form.html', locals())
