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

from closet.models import Closet, Clothe, Type, User

from market.forms import PostForm
from market.models import Cart, Post

#
# 二手拍賣相關頁面
#
# 二手拍賣個人頁面 (mysecondhand)
def get_good_management_page(request):
    posts = SecondHandPost.objects.filter(user=request.user)
    context = {'posts': posts}

    return render(request, 'app/GoodManagemantView.html', context=context)


# 二手拍賣首頁 (secondhand_list)
def list_goods(request):
    posts = SecondHandPost.objects.filter(isSold=False).exclude(user=request.user).order_by('-id')
    context = {'posts': posts}
    return render(request, 'app/GoodsView.html', context=context)


# 二手拍賣貼文頁面 (secondhand)
def get_secondhand_post(request, pk):
    post = SecondHandPost.objects.get(id=pk)
    prob_like_posts = SecondHandPost.objects.filter(
        product__style=post.product.style.first(),
        product__warmness=post.product.warmness,
    ).exclude(user=request.user)
    context = {
        'post': post,
        'prob_like_posts': prob_like_posts,
    }
    return render(request, 'app/GoodView.html', context=context)


# 二手拍賣留言頁面 (second_hand_comments)
def get_secondhand_comments(request, pk):
    comments = SecondHandComment.objects.filter(post=pk)
    context = {'comments': comments}
    return render(request, 'app/GoodCommentView.html', context=context)


# 二手拍賣個人貼文頁面 (mysecondhand_single)
def get_my_single_secondhand(request, pk):
    post = SecondHandPost.objects.get(id=pk)
    context = {
        'post': post,
    }
    return render(request, 'app/GoodPersonalView.html', context=context)


# 二手拍賣新增頁面 (secondhand_create)
class SecondHandPostCreateView(CreateView):

    form_class = PostForm
    template_name = 'app/GoodCreateView.html'

    # FIXME: 目前還沒有做新增圖片，只有新增貼文而已，貼文的圖片還沒新增
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {'user': self.request.user}
        )
        return kwargs

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse('mysecondhand')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clothe = Clothe.objects.get(id=self.kwargs.get('clothePk'))
        context['clothe'] = clothe
        context['my_posts'] = clothe.post_set.all()
        return context


# 二手拍賣修改頁面 (secondhand_update)
class SecondHandPostUpdateView(UpdateView):

    model = Post
    template_name = 'app/GoodUpdateView.html'
    fields = ['title', 'content']

    def get_success_url(self):
        return reverse('clothe', kwargs={'closetPk': self.request.user.closet_set.first().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clothe'] = Clothe.objects.get(id=self.object.product.id)
        return context


# 二手拍賣刪除頁面 (secondhand_delete)
class SecondHandPostDeleteView(DeleteView):

    # TODO: integrate front-end.
    model = Post
    template_name = 'app/_editSecondHandPost.html'

    def get_success_url(self):
        return reverse('clothe', kwargs={'closetPk': self.request.user.closet_set.first().id})


# -------------------------- 分隔線 --------------------------


#
# 購物車相關頁面
#
# 購物車首頁 (cart_list)
class CartListView(ListView):

    # TODO: integrate front-end.
    model = Cart
    template_name = 'app/CartView.html'
    context_object_name = 'carts'

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)


# 購物車詳細頁面 (cart_detail)
class CartDetailView(DetailView):

    model = Cart
    template_name = 'app/CartDetailView.html'
    fields = '__all__'


# 購物車新增頁面 (cart_create)
class CartCreateView(CreateView):

    model = Cart
    template_name = 'app/_editSecondHandPost.html'
    fields = '__all__'

    def get_success_url(self):
        prev_page = self.request.GET.get('prevPage')
        if prev_page:
            return prev_page
        return reverse('cart_list')


# 購物車刪除頁面 (cart_delete)
class CartDeleteView(DeleteView):

    # TODO: integrate front-end
    model = Cart
    template_name = 'app/XXX.html'


# (cart_to_transaction)
class CartToTransactionView(View):

    def get(self, request, *args, **kwargs):
        return redirect(reverse('cart_list'))

    def post(self, request, *args, **kwargs):
        # FIXME: 接下來要處理一些餘額不足的例外情況
        # FIXME: now I assume that one user have only one wallet,
        #        we have to handle the situation that one user have many wallets.
        # FIXME: now I assume that one user have only one closet,
        #        we have to handle the situation that one user have more than one closet.
        selected_carts = request.POST.get('selected_carts', '')
        selected_carts = selected_carts.split(',')
        selected_carts = Cart.objects.filter(id__in=selected_carts)
        for cart in selected_carts:
            buyer = cart.user
            seller = cart.post.user
            amount = cart.post.amount
            product = cart.post.product
            now = arrow.now().datetime

            # update wallet balance.
            buyer_wallet = Wallet.objects.filter(user=buyer).first()
            seller_wallet = Wallet.objects.filter(user=seller).first()
            buyer_wallet.balance -= amount
            seller_wallet.balance -= amount
            buyer_wallet.save()
            seller_wallet.save()

            # update the owneship of the product.
            product.user = buyer
            buyer_closet = Closet.objects.filter(user=buyer).first()
            seller_closet = Closet.objects.filter(user=seller).first()
            buyer_closet.clothes.add(product)
            seller_closet.clothes.remove(product)
            buyer_closet.save()
            seller_closet.save()

            # create transaction log.
            # buyer.
            TransactionLog.objects.create(
                datetime=now,
                log=f'{buyer.nickname} 向 {seller.nickname} 購買了 {cart.post.title}',
                amount=amount,
                wallet=buyer_wallet,
                post=cart.post
            )
            # seller.
            TransactionLog.objects.create(
                datetime=now,
                log=f'{seller.nickname} 向 {buyer.nickname} 賣出了 {cart.post.title}',
                amount=amount,
                wallet=seller_wallet,
                post=cart.post
            )

            # delete the cart.
            cart.delete()

        return redirect('cart_list')


# 交易紀錄頁面 (transaction_list)
def get_transaction_log(request):
    logs = TransactionLog.objects.filter(wallet__user=request.user)
    context = {'logs': logs}
    return render(request, 'app/Transactionlog.html', context=context)


# 錢包頁面 (mywallet)
def get_my_wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    context = {'wallet': wallet}
    return render(request, 'app/MyWallet.html', context=context)


# 錢包設定頁面 (set_wallet)
def set_my_wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    bankaccounts = BankAccount.objects.filter(wallet__user=request.user)
    context = {
        'wallet': wallet,
        'bankaccounts': bankaccounts,
    }
    return render(request, 'app/WalletSetting.html', context=context)


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
