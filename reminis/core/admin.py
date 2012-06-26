from django.contrib import admin
from models import User, Story, TaggedUser, StoryComment

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'full_name')
    search_fields = ('first_name', 'last_name', 'full_name')

class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'authorid', 'title', 'story', 'story_date', 'post_date')
    list_filter = ('authorid',)
    date_hierarchy = 'story_date'
    ordering = ('-story_date',)
    raw_id_fields = ('authorid',)

admin.site.register(TaggedUser)
admin.site.register(StoryComment)
admin.site.register(User, UserAdmin)
admin.site.register(Story, StoryAdmin)