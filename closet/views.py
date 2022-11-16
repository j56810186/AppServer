
import arrow

from pathlib import Path

from django.contrib import auth, messages
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.list import ListView, View
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView

from closet.forms import StyleForm, UserForm
from closet.models import Closet, Clothe, Color, Company, Style, Type, User

from community.models import Post

from market.models import Post as MarketPost

from ai_models.tc_loadmodel import loadClassifyModel
from ai_models.colorClassify_v2 import colorClassify

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
        return render(request, 'closet/ForgotPassword.html')

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
            return render(request, 'closet/ForgotPassword.html')
        return redirect(reverse('login'))


# 風格測驗 (style_form)
class StyleFormView(FormView):

    form_class = StyleForm
    template_name = 'closet/StyleForm.html'

    def form_valid(self, form):
        form.save_result()
        return super().form_valid(form)

    def get_success_url(self):
        return redirect(reverse('clothe',  kwargs={'closetPk': self.user.closet_set.first().id}))


# 使用者資料編輯頁 (edit_user)
class EditUserView(UpdateView):
    model = User
    fields = ['profile_picture', 'username', 'email', 'name', 'phone']
    template_name = 'closet/UserUpdateView.html'

    def get_success_url(self):
        return reverse('settings')


# 用戶設定 (setting)
class SettingView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'closet/PersonalSettings.html')

    def get_success_url(self):
        return reverse('settings')


#
# 衣物管理相關頁面
#
# 衣物首頁 (clothes)
class ClosetView(LoginRequiredMixin, ListView):
    model = Clothe
    template_name = 'closet/ClosetView.html'
    paginate_by = 4

    def get_queryset(self):
        queryset = Closet.objects.filter(user=self.request.user).first().clothes.all()
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
class ShowSingleTypeClotheView(ListView):
    model = Clothe
    template_name = 'closet/ClosetTypeView.html'
    paginate_by = 4
    context_object_name = 'clothes'

    def post(self, *args, **kwargs):
        type_id = self.request.POST.get('type_id')
        if self.request.POST.get('create'):
            closet_name = self.request.POST.get('username')
            new_closet = Closet.objects.create(name=closet_name, user=self.request.user)

            for clothe in self.get_queryset():
                if self.request.POST.get(str(clothe.id)):
                    clothe.closet = new_closet
                    clothe.save()
            
        elif self.request.POST.get('edit'):
            closet = Closet.objects.get(id=self.request.POST.get('closet_id'))
            name = self.request.POST.get('username')
            closet.update(name=name)
            for clothe in self.get_queryset():
                if self.request.POST.get(str(clothe.id)):
                    clothe.closet = new_closet
                    clothe.save()

        return redirect(reverse(
            'single_type_clothes',
            kwargs={
                'typePk': type_id,
            },))

    def get_queryset(self):
        type_id = self.kwargs.get('typePk', None)
        queryset = Clothe.objects.filter(user=self.request.user.id, type=type_id)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        _type = Type.objects.get(id=self.kwargs.get('typePk', None))
        user_closets = Closet.objects.filter(user=self.request.user)
        marketPosts = MarketPost.objects.filter(product__in=self.get_queryset())

        context['type'] = _type
        context['user_closets'] = user_closets
        context['market_posts'] = marketPosts

        return context


# 衣物頁面 (single_clothe)
def show_single_clothe(request, pk):
    clothe = Clothe.objects.get(id=pk)
    related_posts = Post.objects.filter(clothes__in=[clothe])

    context={
        'clothe': clothe,
        'related_posts': related_posts,
    }

    return render(request, 'closet/ClotheView.html', context=context)


# 新增衣物 (create_clothe)
class CreateClotheView(CreateView):
    model = Clothe
    fields = ['user', 'closet', 'image']
    template_name = 'closet/CreateOrEditClotheView.html'

    def post(self, request, *args, **kwargs):
        return CreateView.post(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'edit_clothe',
            kwargs={
                'pk': self.object.id,
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
        if self.request.POST.get('new_image'):
            predict_image(self.object)

        return HttpResponseRedirect(self.get_success_url())




# 編輯衣物 (edit_clothe)
class EditClotheView(UpdateView):
    model = Clothe
    fields = ['name', 'image', 'is_formal', 'warmness', 'color', 'company', 'style', 'shoe_style', 'type', 'note']
    template_name = 'closet/CreateOrEditClotheView.html'
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
            'single_clothe',
            kwargs={
                'pk': self.object.id,
            },
        )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['styles'] = Style.objects.all()
        context_data['colors'] = Color.objects.all()
        context_data['types'] = Type.objects.all()
        context_data['companies'] = Company.objects.all()
        context_data['edit'] = True

        return context_data


# 刪除衣物 (delete_clothe)
class DeleteClotheView(DeleteView):
    model = Clothe
    template_name = 'closet/ClotheDeleteView.html'

    def get_success_url(self):
        return reverse('clothes')


# 新增衣櫃 (create_closet)
class CreateSubClosetView(CreateView):
    model = Closet
    template_name = 'closet/ClosetCreateView.html'
    fields = ['user', 'name']

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

    def get(self, request, *args, **kwargs):
        # refreshSimilarityModel(request)
        context = self.get_context_data(self, request, *args, **kwargs)
        return render(request, 'closet/Recommend.html', context=context)

    def post(self, request, *args, **kwargs):
        used_clothes = request.POST.get('used_clothes', [])
        if used_clothes:
            used_clothes = used_clothes.split(',')
        kwargs['used_clothes'] = used_clothes
        context = self.get_context_data(self, request, *args, **kwargs)

        return render(request, 'closet/Recommend.html', context=context)

    def get_success_url(self):
        return reverse('recommend')

    def get_context_data(self, request, *args, **kwargs):
        used_clothes = kwargs.get('used_clothes', [])
        print(used_clothes)
        context = {}
        clothe = Clothe.objects.get(id=kwargs['pk'])
        recommends = Clothe.objects.filter(
            user=clothe.user,
            style=clothe.style,
        ).exclude(Q(type=clothe.type) | Q(id__in=used_clothes))
        if recommends:
            if len(recommends) > 4:
                recommends = recommends[:4]
        
        used_clothes = ','.join(used_clothes)
        for item in recommends:
            if not used_clothes:
                used_clothes = f'{item.id}'
            used_clothes += f',{item.id}'
        
        context['clothe'] = clothe
        context['recommends'] = recommends
        context['used_clothes'] = used_clothes
        
        return context


# AI models.
CONVERT_PREDICT_COLOR = {
    'Black': 1,
    'White': 2,
    'Blue': 3,
    'Brown': 4,
    'Grey': 5,
    'Red': 6,
    'Green': 7,
    'Navy Blue': 8,
    'Pink': 9,
    'Purple': 10,
    'Silver': 11,
    'Yellow': 12,
    'Beige': 13,
    'Gold': 14,
    'Maroon': 15,
    'Orange': 16,
    'Other': 17
}

CONVERT_PREDICT_TYPE = {
    'shirt': 1,
    'tshirt': 2,
    'pants': 3,
    'shorts': 4,
    'skirt': 5,
    'dress': 6,
    'footwear': 7
}

# ai models.
def predict_image(obj):
    img_path = Clothe.objects.get(id=obj.id).image.path
    pred_type_result = loadClassifyModel(img_path)
    pred_color_result = colorClassify(img_path)
    pred_result = {
        'type': CONVERT_PREDICT_TYPE[pred_type_result],
        'color': CONVERT_PREDICT_COLOR[pred_color_result]
    }
    obj.color = Color.objects.get(id=pred_result['color'])
    obj.type = Type.objects.get(id=pred_result['type'])

    obj.save()










