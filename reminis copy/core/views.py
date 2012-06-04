#from django.template.loader import get_template
#from django.template import Context
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
import datetime, random
from reminis.core.models import User, Story, TaggedUser

from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

#def home(request):
#	return render_to_response('home.html', locals())

@csrf_exempt
def post(request):
    errors = []
    if request.method == 'POST':
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
                          story_date= datetime.datetime.now() - datetime.timedelta(days=365*random.random()))
            story_to_save.save()
                
            errors.append("Sweeeet!! Saved!!!")
            return render_to_response('post.html', {
                                      'errors': errors,
                                      },
                                      RequestContext(request)
                                      )
#            return HttpResponse("Sweeeet!! Saved!!!")
                
    return render_to_response('post.html', {
                              'errors': errors,
                              'authorid': request.POST.get('authorid', ''),
                              'title': request.POST.get('title', ''),
                              'story': request.POST.get('story', ''),
                              },
                              RequestContext(request)
                              )

def search(request):
    if 'q' in request.GET:
        if request.GET['q']:
            query = request.GET['q']
            try:
                user = User.objects.get(fbid=query)
            except User.DoesNotExist:
                error = 'A user with that authorid doesn\'t exist.'
            else:
                stories = Story.objects.filter(authorid = user)
            return render_to_response('search_results.html', locals())
        else:
            return render_to_response('search_form.html', {'error': True})
    else:
        return render_to_response('search_form.html', {'error': False})
