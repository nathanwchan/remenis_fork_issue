from django.contrib import admin
from models import User, Story, TaggedUser, StoryComment, StoryLike, BetaEmail

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'fbid', 'first_name', 'last_name', 'full_name', 'email', 'is_registered')
    search_fields = ('first_name', 'last_name', 'full_name', 'email')

class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'authorid', 'title', 'story', 'story_date_year', 'story_date_month', 'story_date_day', 'post_date', 'is_private')
    list_filter = ('authorid',)
    date_hierarchy = 'post_date'
    ordering = ('-post_date',)
    raw_id_fields = ('authorid',)

class TaggedUserAdmin(admin.ModelAdmin):
    list_display = ('fbid', 'storyid')
    search_fields = ('fbid', 'storyid')
    
class StoryCommentAdmin(admin.ModelAdmin):
    list_display = ('storyid', 'authorid', 'comment', 'post_date')
    search_fields = ('storyid', 'authorid', 'comment', 'post_date')
    
class StoryLikeAdmin(admin.ModelAdmin):
    list_display = ('storyid', 'authorid')
    search_fields = ('storyid', 'authorid')
    
class BetaEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'submit_date')
    date_hierarchy = 'submit_date'
    ordering = ('-submit_date',)
    
admin.site.register(TaggedUser, TaggedUserAdmin)
admin.site.register(StoryComment, StoryCommentAdmin)
admin.site.register(StoryLike, StoryLikeAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(BetaEmail, BetaEmailAdmin)