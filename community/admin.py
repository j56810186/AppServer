from django.contrib import admin
from community.models import Post

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ['id', 'title', 'user']
    list_filter = ['title', 'user']
    list_display = ['id', 'title', 'user']