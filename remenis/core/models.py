from django.db import models
from remenis import settings
from django.db.models import fields

class BigIntegerField(fields.IntegerField):
    
    def db_type(self):
        if settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        else:
            return "bigint"
    
    def get_internal_type(self):
        return "BigIntegerField"
    
    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))
            
class User(models.Model):
    fbid = models.CharField(max_length=20)
    facebook_id = models.IntegerField(default=0, primary_key=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    is_registered = models.BooleanField()
    last_date = models.DateTimeField(blank=True, null=True)
    page_views = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)
    
    class Admin:
        pass

class Story(models.Model):
    authorid = models.ForeignKey(User)
    title = models.CharField(max_length=100, blank=True)
    story = models.TextField()
    story_date_year = models.IntegerField(blank=True, null=True)
    story_date_month = models.IntegerField(blank=True, null=True)
    story_date_day = models.IntegerField(blank=True, null=True)
    post_date = models.DateTimeField(blank=True, null=True)
    is_private = models.BooleanField()
    page_views = models.IntegerField(default=0)
    fbid_for_migration = models.BigIntegerField(default=0)
    
    class Admin:
        pass
    
class TaggedUser(models.Model):
    storyid = models.ForeignKey(Story)
    taggeduserid = models.ForeignKey(User, blank=True, null=True)
    fbid_for_migration = models.BigIntegerField(default=0)
        
    class Admin:
        pass

class StoryComment(models.Model):
    storyid = models.ForeignKey(Story)
    authorid = models.ForeignKey(User, blank=True, null=True)
    comment = models.TextField()
    post_date = models.DateTimeField(blank=True, null=True)
    fbid_for_migration = models.BigIntegerField(default=0)
    
    class Admin:
        pass

class StoryLike(models.Model):
    storyid = models.ForeignKey(Story)
    authorid = models.ForeignKey(User)
    fbid_for_migration = models.BigIntegerField(default=0)
    
    class Admin:
        pass
        
class BetaEmail(models.Model):
    email = models.EmailField(blank=True, null=True)
    submit_date = models.DateTimeField(blank=True, null=True)
    
    class Admin:
        pass