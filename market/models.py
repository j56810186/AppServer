
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save


from closet.models import Clothe, User
from community.models import BaseComment, BasePost


class Post(BasePost):

    USED_CHOICES = (
        (1, 'Well-used'),
        (2, 'Used'),
        (3, 'New')
    )

    used = models.IntegerField(choices=USED_CHOICES)
    amount = models.IntegerField()
    is_sold = models.BooleanField(default=False)

    # foreign key.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='market_posts')
    product = models.ForeignKey(Clothe, on_delete=models.CASCADE, related_name='market_posts')


class PostImage(models.Model):

    # image.
    image = models.ImageField(upload_to='images/second_hand_posts')

    # foreign key.
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')


class Comment(BaseComment):

    # Foreign key.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='_market_comments')
    likes = models.ManyToManyField(User, blank=True, null=True, related_name='_market_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, related_name='comments')


class Wallet(models.Model):

    name = models.CharField(max_length=50)
    balance = models.IntegerField()

    # Foreign key.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')


@receiver(post_save, sender=User)
def create_new_closet(instance, **kwargs):
    if kwargs.get('created', None):
        Wallet.objects.create(
            name=f"{instance.username}'s wallet",
            balance=0,
            user=instance,
        )


class Bank(models.Model):

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5)


class BankAccount(models.Model):

    accountName = models.CharField(max_length=50)
    account = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)

    # Foreign keys.
    bank = models.ForeignKey('Bank', on_delete=models.CASCADE)
    wallet = models.ForeignKey('Wallet', on_delete=models.CASCADE, related_name='bank_account')


class TransactionLog(models.Model):

    ''' Models' settings. '''
    PAYMENT_CHOICES = (
        (1, '貨到付款'),
        (2, '錢包付款'),
    )

    datetime = models.DateTimeField()
    log = models.CharField(max_length=100)
    amount = models.IntegerField()
    payment = models.IntegerField(choices=PAYMENT_CHOICES)
    address = models.CharField(max_length=100)
    done = models.BooleanField()

    # Foreign key.
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bought_transaction')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_transaction')


class Cart(models.Model):

    ''' Model's settings. '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

