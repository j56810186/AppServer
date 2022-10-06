import arrow

from pathlib import Path

from django.contrib import auth, messages
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.list import ListView, View
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from closet.models import Clothe, Type

from market.forms import PostForm
from market.models import BankAccount, Cart, Comment, Post, TransactionLog, Wallet

#
# 二手拍賣相關頁面
#
# 二手拍賣個人頁面 (mysecondhand)
def get_my_products(request):
    posts = Post.objects.filter(user=request.user)
    context = {'posts': posts}

    return render(request, 'market/GoodManagementView.html', context=context)


# 二手拍賣首頁 (secondhand_list)
def get_products(request):
    posts = Post.objects.filter(is_sold=False).exclude(user=request.user).order_by('-id')
    context = {'posts': posts}
    return render(request, 'market/GoodsView.html', context=context)


# 二手拍賣貼文頁面 (secondhand)
def get_product(request, pk):
    post = Post.objects.get(id=pk)
    prob_like_posts = Post.objects.filter(
        product__style=post.product.style,
        product__warmness=post.product.warmness,
    ).exclude(user=request.user)
    comments = Comment.objects.filter(post=pk).order_by('-id')
    if comments and len(comments) > 2:
        comments = Comment.objects.filter(post=pk).order_by('-id')[:2]

    context = {
        'post': post,
        'prob_like_posts': prob_like_posts,
        'comments': comments,
    }
    return render(request, 'market/GoodView.html', context=context)


# 二手拍賣留言頁面 (second_hand_comments)
def get_product_comments(request, pk):
    if request.method == 'GET':
        post = Post.objects.get(id=pk)
        comments = Comment.objects.filter(post=pk)
        context = {
            'comments': comments,
            'post': post,
        }
        return render(request, 'market/GoodCommentView.html', context=context)
    else:
        comment = request.POST.get('comment', None)
        if comment:
            Comment.objects.create(
                user=request.user,
                text=comment,
                datetime=arrow.now().datetime,
                post=Post.objects.get(id=pk),
            )

        redirect_to = request.GET.get('prev_page', None)
        if redirect_to:
            return redirect(redirect_to)
        else:
            return redirect('product_comments', pk=pk)

# 二手拍賣個人貼文頁面 (mysecondhand_single)
def get_my_product(request, pk):
    post = Post.objects.get(id=pk)
    context = {
        'post': post,
    }
    return render(request, 'market/GoodPersonalView.html', context=context)


# 二手拍賣新增頁面 (secondhand_create)
class PostCreateView(CreateView):

    form_class = PostForm
    template_name = 'market/GoodCreateView.html'

    # FIXME: 目前還沒有做新增圖片，只有新增貼文而已，貼文的圖片還沒新增
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {'user': self.request.user}
        )
        return kwargs

    def get_success_url(self):
        return reverse('my_product', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clothe = Clothe.objects.get(id=self.kwargs.get('clothePk'))
        context['clothe'] = clothe
        context['my_posts'] = clothe.post_set.all()
        return context


# 二手拍賣修改頁面 (secondhand_update)
class PostUpdateView(UpdateView):

    model = Post
    template_name = 'market/GoodUpdateView.html'
    fields = ['title', 'content', 'amount', 'used']
    context_object_name = 'post'

    def get_success_url(self):
        return reverse('my_product', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clothe'] = Clothe.objects.get(id=self.object.product.id)
        return context


# 二手拍賣刪除頁面 (secondhand_delete)
class PostDeleteView(DeleteView):

    # TODO: integrate front-end.
    model = Post
    template_name = 'app/_editPost.html'

    def get_success_url(self):
        return reverse('my_products')


# -------------------------- 分隔線 --------------------------


#
# 購物車相關頁面
#
# 購物車首頁 (cart_list)
class CartListView(ListView):

    # TODO: integrate front-end.
    model = Cart
    template_name = 'market/CartsView.html'
    context_object_name = 'carts'

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)


# 購物車新增頁面 (cart_create)
class CartCreateView(CreateView):

    model = Cart
    template_name = 'app/_editPost.html'
    fields = '__all__'

    def get_success_url(self):
        prev_page = self.request.GET.get('prevPage')
        if prev_page:
            return prev_page
        return reverse('cart_list')


# 購物車刪除頁面 (cart_delete)
class CartDeleteView(DeleteView):

    model = Cart

    def get_success_url(self):
        return reverse('carts')


# (cart_to_transaction)
class CartToTransactionView(View):

    def get(self, request, *args, **kwargs):
        selected_carts = request.GET.get('selected_carts', '')
        payment_choices = TransactionLog.PAYMENT_CHOICES
        context = {
            'selected_carts': selected_carts,
            'payment_choices': payment_choices,
        }
        return render(request, 'market/CartToTransactionView.html', context=context)

    def post(self, request, *args, **kwargs):
        # FIXME: 接下來要處理一些餘額不足的例外情況
        # FIXME: now I assume that one user have only one wallet,
        #        we have to handle the situation that one user have many wallets.
        # FIXME: now I assume that one user have only one closet,
        #        we have to handle the situation that one user have more than one closet.
        # breakpoint()
        selected_carts = request.POST.get('selected_carts', '')
        selected_carts = selected_carts.split(',')
        selected_carts = Cart.objects.filter(id__in=selected_carts)
        for cart in selected_carts:
            buyer = cart.user
            seller = cart.post.user
            amount = cart.post.amount
            product = cart.post.product
            payment = request.POST.get('payment', None)
            post = cart.post
            now = arrow.now().datetime

            # update wallet balance.
            buyer_wallet = buyer.wallets.first()
            if payment == 2:
                buyer_wallet.balance -= amount
                buyer_wallet.save()

            # update the owneship of the product.
            product.user = buyer
            product.closet = buyer.closets.first()
            product.save()

            # create transaction log.
            # buyer.
            TransactionLog.objects.create(
                datetime=now,
                log=f'{buyer.name} 向 {seller.name} 購買了 {cart.post.title}',
                amount=amount,
                payment=payment,
                address=request.POST.get('address', None),
                done=False,
                wallet=buyer_wallet,
                post=cart.post,
                buyer=buyer,
                seller=seller,
            )
            # seller.
            TransactionLog.objects.create(
                datetime=now,
                log=f'{seller.name} 向 {buyer.name} 賣出了 {cart.post.title}',
                amount=amount,
                payment=payment,
                address=request.POST.get('address', None),
                done=True,
                wallet=seller.wallets.first(),
                post=cart.post,
                buyer=buyer,
                seller=seller,
            )

            # set the secondhand post sold.
            post.is_sold = True
            post.save()

            # delete the cart.
            cart.delete()

        return redirect('carts')


# 交易紀錄頁面 (transaction_list)
def get_transaction_log(request):
    logs = TransactionLog.objects.filter(wallet__user=request.user)
    context = {'logs': logs}
    return render(request, 'market/TransactionLogs.html', context=context)


def get_single_transaction_log(request, pk):
    log = TransactionLog.objects.get(id=pk)
    payment = TransactionLog.PAYMENT_CHOICES[log.payment - 1][1]
    context = {
        'log': log,
        'payment': payment,
    }
    if request.method == 'POST':
        done = request.POST.get('done', None)
        if done:
            log.done = True
            seller_wallet = log.seller.wallets.first()
            seller_wallet.balance += log.amount
            seller_wallet.save()

    return render(request, 'market/TransactionLog.html', context=context)


# 錢包頁面 (mywallet)
def get_my_wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    context = {'wallet': wallet}
    return render(request, 'market/WalletView.html', context=context)


# 錢包設定頁面 (set_wallet)
def set_my_wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    bankaccounts = BankAccount.objects.filter(wallet__user=request.user)
    context = {
        'wallet': wallet,
        'bankaccounts': bankaccounts,
    }
    return render(request, 'market/WalletEditView.html', context=context)


# -------------------------- 分隔線 --------------------------


#
# 其他函數
#
# 衣物辨識模型函數
def predict_image(obj):
    # FIXME: 最好調整一下 CLASSIFIER 的操作，這樣不好用，而且現在的 code 好醜，跟瀞之討論之後再看看怎麼調是最好的
    img_path = Clothe.objects.get(id=obj.id).image.path
    pred_type_result = loadClassifyModel(img_path)
    pred_color_result = colorClassify(img_path)
    pred_result = {
        'type': CONVERT_PREDICT_TYPE[pred_type_result],
        'color': CONVERT_PREDICT_COLOR[pred_color_result]
    }
    print(CONVERT_PREDICT_COLOR[pred_color_result])
    obj.color.add(Color.objects.get(id=pred_result['color']))
    obj.type = Type.objects.get(id=pred_result['type'])

    obj.save()


# 相似度模型刷新
def refresh_similarity_model(request):
    user = request.user
    model = Clothe.objects.filter(user=user).first()
    path = Path(model.image.path)
    print(path.parent.absolute())
    findsimilar.refreshSimilarityModel(path.parent.absolute(), user.id)
