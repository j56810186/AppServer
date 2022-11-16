
from django.db import models

from closet.models import User, Clothe

''' Base Post model, all Post are inherit this models. '''
class BasePost(models.Model):

    title = models.CharField(max_length=25)
    content = models.TextField()
    datetime = models.DateTimeField()

    class Meta():
        abstract = True


class Post(BasePost):

    image = models.ImageField(upload_to='images/posts')

    # Foreign key.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    follower = models.ManyToManyField(User, related_name='followedPosts')
    likes = models.ManyToManyField(User, blank=True)
    clothes = models.ManyToManyField(Clothe, blank=True, null=True)


''' Base Comment model, all Comment are inherit this models. '''
class BaseComment(models.Model):

    text = models.TextField()
    datetime = models.DateTimeField()

    class Meta():
        abstract = True


class Comment(BaseComment):

    # Foreign keys.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='_comments')
    likes = models.ManyToManyField(User, blank=True, null=True, related_name='_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, related_name='comments')
