
from django.urls import path

import community.views as views


urlpatterns = [
    # 社群頁面
    path('<int:pk>/profile', views.profile, name='profile'),

    path('my-outfits/', views.get_personal_outfits, name='personal_outfits'),
    path('saved-get_personal_outfits', views.saved_outfits, name='saved_outfits'),

    path('outfits/', views.OutfitView.as_view(), name='outfits'),
    path('outfits/<int:pk>', views.outfit, name='outfit'),
    path('outfits/create', views.CreateOutfitView.as_view(), name='create_outfit'),
    path('outfits/create/<int:clotheId>', views.CreateOutfitView.as_view(), name='create_outfit_with_clothe'),
    path('outfits/<int:pk>/edit', views.EditOutfitView.as_view(), name='edit_outfit'),
    path('outfits/<int:pk>/delete', views.DeleteOutfitView.as_view(), name='delete_outfit'),
    path('outfits/<int:postPk>/comments', views.comments, name='outfit_comments'),
    path('outfits/<int:postPk>/remake', views.remake_outfit, name='remake_outfit'),
    path('outfits/<int:postPk>/remake/select', views.select_remake_outfit, name='select_remake'),
]
