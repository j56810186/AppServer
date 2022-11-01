
import arrow
import os

from pathlib import Path

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.list import ListView, View
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from closet.models import Closet, Clothe
from community.models import Comment, Post


# 個人頁面 (profile)
def profile(request, pk):
    user = request.user
    posts = Post.objects.filter(user=user)
    user_closets = Closet.objects.filter(user_id=user.id)
    return render(request, 'community/Profile.html', context={'posts': posts, 'user_closets': user_closets})
# FIXME: profile 怎麼會是 settings 頁面？
# 這個好像應該要改成一個 user 的 profile 才對



#
# 社群相關頁面
#
# 穿搭首頁 (personal_outfits)
def get_personal_outfits(request):
    user = request.user
    user_closets = Closet.objects.filter(user_id=user.id)
    posts = Post.objects.filter(user=user)

    if request.method == 'POST':
        outfit = Post.objects.get(id=request.POST['postPk'])
        outfit.delete()

    return render(request, 'community/OutfitPersonalView.html', context={'posts': posts, 'user_closets': user_closets})


# 收藏穿搭頁面 (saved_outfits)
def saved_outfits(request):
    return render(request, 'community/SavedOutfitView.html')


# 探索穿搭頁面 (get_personal_outfits)
class OutfitView(ListView):
    model = Post
    template_name = 'community/OutfitsView.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user_closets = Closet.objects.filter(user_id=self.request.user.id)
        context['user_closets'] = user_closets
        return context

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().get(request)

    def post(self, request):
        user = request.user
        _post = Post.objects.get(id=request.POST['post_id'])
        comment = request.POST.get('comment', None)
        like = request.POST.get('like', None)
        followed = request.POST.get('followed', None)
        time = arrow.now()

        if comment:
            new_comment = Comment(text=comment, datetime=time.format('YYYY-MM-DD HH:MM'), user=user, post=post)
            new_comment.save()

        if like:
            _post.likes.add(user)
            _post.save()

        if followed:
            user.followedPosts.add(_post)
            user.save()

        return redirect(reverse('outfits'))


# 穿搭頁面 (outfit)
def outfit(request, pk):
    post = Post.objects.get(id=pk)

    if request.method == 'POST':
        user = request.user
        comment = request.POST.get('comment', None)
        like = request.POST.get('like', None)
        followed = request.POST.get('followed', None)
        time = arrow.now()

        if comment:
            new_comment = Comment(text=comment, datetime=time.format('YYYY-MM-DD HH:MM'), user=user, post=post)
            new_comment.save()

        if like:
            post.likes.add(user)
            post.save()

        if followed:
            user.followedPosts.add(post)
            user.save()

        return redirect(reverse('outfit', kwargs={'pk': post.id}))

    return render(request, 'community/OutfitView.html', context={'post': post})


# 新增穿搭 (create_outfit)
class CreateOutfitView(CreateView):
    model = Post
    fields = ['title', 'content', 'image']
    template_name = 'community/OutfitCreateView.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['clothes'] = Clothe.objects.filter(user=self.request.user)

        return context_data

    def post(self, request, *args, **kwargs):
        content = request.POST['content']
        tag = request.POST['title']
        image = request.FILES['image']
        now = arrow.now()

        new_post = Post(title=tag, content=content, image=image, datetime=now.datetime, user=request.user)
        new_post.save()

        c = Clothe.objects.filter(user=self.request.user)
        for i, clothe in enumerate(c):
            if request.POST.get(f'clothe{i + 1}') == 'on':
                new_post.clothes.add(clothe)
        new_post.save()

        user_closets = Closet.objects.filter(user_id=self.request.user.id)
        return redirect(reverse('personal_outfits'))

    def get_success_url(self):
        user_closets = Closet.objects.filter(user_id=self.request.user.id)

        return redirect(reverse('personal_outfits'))


# 編輯、刪除穿搭 (edit_outfit)
class EditOutfitView(UpdateView):
    model = Post
    fields = ['title', 'image', 'content', 'clothes']
    template_name = 'community/OutfitUpdateView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.get(id=self.object.id)
        context['clothes'] = Clothe.objects.filter(user=self.request.user)
        return context

    def get_success_url(self):
        user_closets = Closet.objects.filter(user_id=self.request.user.id)

        return reverse(
            'personal_outfits',
        )


# 留言頁面 (comments)
def comments(request, postPk):
    _post = Post.objects.get(id=postPk)

    if request.method == 'POST':
        user = request.user
        _post = Post.objects.get(id=request.POST['post_id'])
        comment = request.POST.get('comment', None)
        time = arrow.now()
        print('c', comment)
        if comment:
            new_comment = Comment(text=comment, time=time.format('HH:MM'), user=user)
            new_comment.save()
            _post.comments.add(new_comment)
            _post.save()

        return redirect(reverse('outfit_comments', kwargs={'postPk': _post.id}))

    return render(request, 'community/OutfitCommentView.html', context={'post': _post})

# 復刻穿搭頁面 (remake_outfit)
def remake_outfit(request, postPk):
    user = request.user
    post = Post.objects.get(id=postPk)
    user_closets = Closet.objects.filter(user_id=user.id)
    return render(request, 'community/OutfitRemakeView.html', context={'post': post, 'user_closets': user_closets})


# 復刻穿搭選擇頁面 (select_remake)
def select_remake_outfit(request, postPk):
    # user = request.user
    # post = Post.objects.get(id=postPk)
    # user_closets = Closet.objects.filter(user_id=user.id)
    # model = Clothe.objects.filter(user=user).first()
    # path = Path(model.image.path)
    # p = str(path.absolute())
    # findsimilar.selectarea(p)

    # The following lines are the steps to make the similarity modle work.
    # 1. if user post `refresh`, then I should query all the user's clothes
    #    and the image path.
    # 2. copy these images to a dir which contains all this user's clothes' image.
    # 3. name the dir `{user_id}`
    # 4. call command and add `refresh` param in it.
    # 5. if user did NOT post `refresh`, then i should just call command.

    # Somethings that maybe concerned: 
    # 1. how to cut the clothe image from the outfit image.
    # 2. from the above line, save the result of cutting image.
    # that all i have thought.


    command = f'python {Path(settings.BASE_DIR, "ai_models/findsimilar.py")} 1 gggg --refresh=1'
    result = os.popen(command).read()
    return HttpResponse(result)
    
    # return render(request, 'community/OutfitSelectRemakeView.html', context={'post': post, 'user_closets': user_closets})
