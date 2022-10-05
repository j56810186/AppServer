
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

from closet.forms import StyleForm, UserForm
from closet.models import Closet, Clothe, Type, User


#
# 個人相關頁面
#
# 登入頁 (login)
class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('clothes')
        return render(request, 'closet/Login.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('clothes'))

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)

            # 登入成功 導向首頁
            if user.is_active:
                message = '登入成功！'
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('clothes'))

            # 第一次登入成功 導向風格頁面
            else:
                message = '首次登入，請完成風格測驗！'
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('styleForm'))

        # 登入失敗
        else:
            message = '登入失敗，請確認帳號與密碼後重新嘗試！'
            return render(request, 'closet/Login.html', locals())


# 登出頁 (logout)
class LogoutView(View):

    def get(self, request):
        auth.logout(request)
        return redirect(reverse('login'))


# 註冊頁 (register)
def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            username = request.POST['username']
            password = request.POST['password2']
            user = authenticate(request, username=username, password=password)

            # create new closet and wallet for this new user with signal.

            return redirect(reverse('login'))

    else:
        form = UserForm()

    context = {'form': form}
    return render(request, 'closet/Register.html', context=context)


# 忘記密碼頁 (forgot_password)
class ForgotPasswordView(View):

    def get(self, request):
        return render(request, 'app/ForgotPassword.html')

    def post(self, request):
        email = request.POST['email']
        user = User.objects.get(email=email)
        if user:
            print('send email')
            send_mail(
                '這是一封驗證信',
                '這是驗證信的內容',
                'nccumis@nccu.edu.tw',
                [email],
            )
            message = '成功寄出驗證信！請在您的信箱確認！'
        else:
            message = '驗證信寄出失敗，請確認是否使用此信箱註冊！'
            return render(request, 'app/ForgotPassword.html')
        return redirect(reverse('login'))


# 風格測驗 (style_form)
class StyleFormView(FormView):

    form_class = StyleForm
    template_name = 'app/StyleForm.html'

    def form_valid(self, form):
        form.save_result()
        return super().form_valid(form)

    def get_success_url(self):
        return redirect(reverse('clothe',  kwargs={'closetPk': user.closet_set.first().id}))


# 使用者資料編輯頁 (edit_user)
class EditUserView(UpdateView):
    model = User
    fields = ['username', 'email', 'nickname', 'phone']
    template_name = 'app/ProfileUpdateView.html'

    def get_success_url(self):
        return reverse('profile')


# 用戶設定 (setting)
class SettingView(View):

    def get(self, request):
        return render(request, 'app/Setting.html')

    def get_success_url(self):
        return reverse('setting')


#
# 衣物管理相關頁面
#
# 衣物首頁 (clothes)
class ClosetView(LoginRequiredMixin, ListView):
    model = Clothe
    template_name = 'closet/ClosetView.html'
    paginate_by = 4

    def get_queryset(self):
        queryset = Closet.objects.get(user=self.request.user).clothes.all()
        return queryset

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        context = super().get_context_data(*args, **kwargs)
        user_closets = Closet.objects.filter(user_id=user.id)
        types = Type.objects.all()
        clothes = Clothe.objects.filter(user_id=self.request.user.id)

        context['user_closets'] = user_closets
        context['types'] = types
        context['clothes'] = clothes

        # Every types of clothes
        t_shirts = Clothe.objects.filter(user_id=user.id).filter(type_id=2)
        shirts = Clothe.objects.filter(user_id=user.id).filter(type_id=1)
        shorts = Clothe.objects.filter(user_id=user.id).filter(type_id=4)
        pants = Clothe.objects.filter(user_id=user.id).filter(type_id=3)
        skirts = Clothe.objects.filter(user_id=user.id).filter(type_id=5)
        dresses = Clothe.objects.filter(user_id=user.id).filter(type_id=6)
        shoes = Clothe.objects.filter(user_id=user.id).filter(type_id=7)

        context['t_shirts'] = t_shirts
        context['shirts'] = shirts
        context['shorts'] = shorts
        context['pants'] = pants
        context['skirts'] = skirts
        context['dresses'] = dresses
        context['shoes'] = shoes

        return context


#
# 衣物管理相關頁面
#
# 衣物首頁 (clothes)
class ClotheView(ListView):
    model = Clothe
    template_name = 'app/ClosetView.html'
    paginate_by = 4

    def get_queryset(self):
        closet_id = self.kwargs.get('closetPk', None)
        queryset = Closet.objects.get(id=closet_id).clothes.all()
        return queryset

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        context = super().get_context_data(*args, **kwargs)
        user_closets = Closet.objects.filter(user_id=user.id)
        types = Type.objects.all()
        clothes = Clothe.objects.filter(user_id=self.request.user.id)

        context['user_closets'] = user_closets
        context['types'] = types
        context['clothes'] = clothes

        # Every types of clothes
        t_shirts = Clothe.objects.filter(user_id=user.id).filter(type_id=2)
        shirts = Clothe.objects.filter(user_id=user.id).filter(type_id=1)
        shorts = Clothe.objects.filter(user_id=user.id).filter(type_id=4)
        pants = Clothe.objects.filter(user_id=user.id).filter(type_id=3)
        skirts = Clothe.objects.filter(user_id=user.id).filter(type_id=5)
        dresses = Clothe.objects.filter(user_id=user.id).filter(type_id=6)
        shoes = Clothe.objects.filter(user_id=user.id).filter(type_id=7)

        context['t_shirts'] = t_shirts
        context['shirts'] = shirts
        context['shorts'] = shorts
        context['pants'] = pants
        context['skirts'] = skirts
        context['dresses'] = dresses
        context['shoes'] = shoes

        return context


# 衣物分頁 (single_type_clothes)
class ShowSingleClotheView(ListView):
    model = Clothe
    template_name = 'app/ClosetTypeView.html'
    paginate_by = 4

    def get_queryset(self):
        closet_id = self.kwargs.get('closetPk', None)
        queryset = Closet.objects.get(id=closet_id).clothes.all()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        user_closets = Closet.objects.filter(user_id=self.request.user.id)
        type = Type.objects.get(id=self.kwargs.get('typePk', None))
        clothes = user_closets.get(id=self.kwargs.get('closetPk', None)).clothes.filter(type_id=type.id)

        context['user_closets'] = user_closets
        context['type'] = type
        context['clothes'] = clothes

        return context


# 衣物頁面 (single_clothe)
def show_single_clothe(request, closetPk, clothePk):
    closet = Closet.objects.get(id=closetPk)
    clothe = Clothe.objects.get(id=clothePk)
    related_posts = Post.objects.filter(clothes__in=[clothe])

    context={
        'closet': closet,
        'clothe': clothe,
        'related_posts': related_posts,
    }

    return render(request, 'app/ClotheView.html', context=context)


# 新增衣物 (create_clothe)
class CreateClotheView(CreateView):
    model = Clothe
    fields = ['image']
    template_name = 'app/ClotheCreateView.html'

    def post(self, request, *args, **kwargs):
        return CreateView.post(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'editClothe',
            kwargs={
                'pk': self.object.id,
                'closetPk': self.object.closet_set.first().id
            }
        )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['styles'] = Style.objects.all()
        context_data['colors'] = Color.objects.all()
        context_data['types'] = Type.objects.all()
        context_data['companies'] = Company.objects.all()
        user_closets = Closet.objects.filter(user_id=self.request.user.id)
        context_data['user_closets'] = user_closets

        return context_data

    def form_valid(self, form):
        self.object = form.save()
        obj = self.object
        obj.closet_set.add(self.request.user.closet_set.first())
        if self.request.POST.get('new_image'):
            predict_image(obj)
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


# 編輯衣物 (edit_clothe)
class EditClotheView(UpdateView):
    model = Clothe
    fields = ['name', 'image', 'isFormal', 'warmness', 'color', 'company', 'style', 'shoeStyle', 'type', 'note']
    template_name = 'app/AddNewClothes.html'
    context_object_name = 'clothe'
    # template_name = 'app/ClotheUpdateView.html'

    def form_invalid(self, form):
        if not form.cleaned_data['image']:
            form.cleaned_data['image'] = self.get_object().image
        return UpdateView.form_invalid(self, form)

    def form_valid(self, form):
        self.object = form.save()
        object = self.object
        if self.request.POST.get('new_image'):
            predict_image(object)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'viewClothe',
            kwargs={
                'closetPk': self.request.user.closet_set.first().id, # FIXME: self.object.closet_set.first().id,
                'clothePk': self.object.id,
            },
        )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['styles'] = Style.objects.all()
        context_data['colors'] = Color.objects.all()
        context_data['types'] = Type.objects.all()
        context_data['companies'] = Company.objects.all()

        return context_data


# 刪除衣物 (delete_clothe)
class DeleteClotheView(DeleteView):
    model = Clothe
    template_name = 'app/ClotheDeleteView.html'

    def get_success_url(self):
        return reverse('clothe', kwargs={'closetPk': self.request.user.closet_set.first().id})


# 新增衣櫃 (create_closet)
class CreateSubClosetView(CreateView):
    model = Closet
    template_name = 'app/ClosetCreateView.html'
    fields = ['user', 'name', 'clothes']

    def get_success_url(self):
        user_closets = Closet.objects.filter(user_id=self.kwargs.get('userPk', None))
        return reverse(
            'clothe',
            kwargs={
                'closetPk': user_closets.first().id,
            }
        )


# 穿搭推薦 (recommend)
class RecommendView(View):

    def get(self, request):
        # refreshSimilarityModel(request)
        return render(request, 'app/Recommend.html')

    def get_success_url(self):
        return reverse('recommend')














