
from django.urls import path

from django.views.generic.base import RedirectView
from django.urls import reverse

import closet.views as views


urlpatterns = [
    # 個人相關頁面
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('register', views.register, name='register'),
    path('forgotpassword', views.ForgotPasswordView.as_view(), name='forgot_password'),
    
    path('styleform', views.StyleFormView.as_view(), name='style_form'),

    path('<int:pk>/edit', views.EditUserView.as_view(), name='edit_user'),
    path('<int:pk>/settings', views.SettingView.as_view(), name='setting'),

    # 衣物管理頁面
    path('clothes/', views.ClosetView.as_view(), name='clothes'),
    path('clothes/create', views.CreateClotheView.as_view(), name='create_clothe'),
    
    path('clothes/type/<int:typePk>', views.ShowSingleClotheView.as_view(), name='single_type_clothes'),
    path('clothes/<int:clothePk>', views.show_single_clothe, name='single_clothe'),
    
    path('clothes/<int:pk>/edit', views.EditClotheView.as_view(), name='edit_clothe'),
    path('clothes/<int:pk>/delete', views.DeleteClotheView.as_view(), name='delete_clothe'),
    path('closet/create', views.CreateSubClosetView.as_view(), name='create_closet'),
    path('recommend', views.RecommendView.as_view(), name='recommend'),
    
    path('', RedirectView.as_view(url='closet'), name='root'),
]
