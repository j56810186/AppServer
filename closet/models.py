
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):

    # Remove some columns that we don't need.
    first_name = None
    last_name = None

    # Customize some existed columns.
    username = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=50)

    # Add our columns.
    name = models.CharField(max_length=15, null=True, blank=True, default='新使用者')
    phone = models.CharField(max_length=10, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='images/profile_pictures', default=None, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)

    # Set REQUIRED_FIELDS.
    REQUIRED_FIELDS = []

    # Replace the USER_NAME_FIELD.
    USERNAME_FIELD = 'username'

    # Set objects.
    objects = UserManager()

    # Foreign key.
    friends = models.ManyToManyField('User')


class Closet(models.Model):

    # Self settings.
    name = models.CharField(max_length=15, default='我的衣櫃', null=True, blank=True)

    # Foreign key setting.
    user = models.ForeignKey('User', on_delete=models.CASCADE)

@receiver(post_save, sender=User)
def create_new_closet(instance, **kwargs):
    if kwargs.get('created', None):
        Closet.objects.create(
            name=f'{instance.username} 的衣櫃',
            user=instance,
        )


class Clothe(models.Model):

    # Choices
    FORMAL_CHOICES = [
        (True, '正式'),
        (False, '休閒')
    ]

    WARMNESS_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    ]

    # Self settings.
    name = models.CharField(max_length=50, default='', blank=True, null=True)
    image = models.ImageField(upload_to='images/clothes')
    warmness = models.IntegerField(choices=WARMNESS_CHOICES, default=3, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    is_formal = models.BooleanField(choices=FORMAL_CHOICES, default=False, blank=True, null=True)
    is_public = models.BooleanField(default=False, blank=True, null=True)

    # Foreign keys.
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    closet = models.ForeignKey('Closet', on_delete=models.CASCADE, related_name='clothes')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey('Type', on_delete=models.CASCADE, blank=True, null=True)
    style = models.ForeignKey('Style', on_delete=models.CASCADE, blank=True, null=True)
    shoe_style = models.ForeignKey('ShoeStyle', on_delete=models.CASCADE, blank=True, null=True)


class Company(models.Model):

    name = models.CharField(max_length=50)
    url = models.URLField()

    def __str__(self):
        return self.name


class Type(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Style(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ShoeStyle(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Color(models.Model):

    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.name
