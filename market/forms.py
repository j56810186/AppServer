
import arrow

from django import forms

from market.models import Post


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Post
        fields = ('title', 'content', 'amount', 'product', 'is_sold')

    def save(self, commit=False):
        obj = super().save(commit=False)
        obj.time = arrow.now().datetime
        obj.user = self.user
        obj.save()
        return obj
