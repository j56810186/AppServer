
from django.urls import path

import community.views as views


urlpatterns = [
    # 社群頁面
    path('<int:pk>/profile', views.profile, name='profile'),

    path('<int:userPk>/outfits', views.outfits, name='personal_outfits'),
    path('<int:userPk>/savedoutfits', views.saved_outfits, name='saved_outfits'),
    path('outfits', views.OutfitView.as_view(), name='outfits'),
    path('outfits/<int:pk>', views.outfit, name='outfit'),
    path('outfits/create', views.CreateOutfitView.as_view(), name='create_outfit'),
    path('outfits/<int:pk>/edit', views.EditOutfitView.as_view(), name='edit_outfit'),
    path('outfits/<int:postPk>/comments', views.comments, name='comments'),
    path('outfits/<int:postPk>/remake', views.remake_outfit, name='remake_outfit'),
    path('outfits/<int:postPk>/remake/select', views.select_remake_outfit, name='select_remake'),
]
