
from django.urls import path

import market.views as views


urlpatterns = [
    # 二手拍賣頁面
    path('mysecondhand', views.get_good_management_page, name='my_products'),
    path('mysecondhand/<int:pk>', views.get_my_single_secondhand, name='my_product'),
    path('secondhand', views.list_goods, name='products'),
    path('secondhand/<int:pk>', views.get_secondhand_post, name='product'),
    path('secondhand/<int:pk>/comments', views.get_secondhand_comments, name='product_post_comments'),
    path('secondhand/<int:clothePk>/create', views.SecondHandPostCreateView.as_view(), name='product_post_create'),
    path('secondhand/<int:pk>/edit', views.SecondHandPostUpdateView.as_view(), name='product_post_update'),
    path('secondhand/<int:pk>/delete', views.SecondHandPostDeleteView.as_view(), name='product_post_delete'),


    # 購物車
    path('cart', views.CartListView.as_view(), name='cart_list'),
    path('cart/<int:pk>', views.CartDetailView.as_view(), name='cart_detail'),
    path('cart/<int:pk>/delete', views.CartDeleteView.as_view(), name='cart_delete'),
    path('cart/create', views.CartCreateView.as_view(), name='cart_create'),
    path('cart/trasaction', views.CartToTransactionView.as_view(), name='cart_to_transaction'),
    path('transactionlog', views.get_transaction_log, name='transactionlog_list'), # 交易紀錄
    path('mywallet', views.get_my_wallet, name='my_wallet'), # 錢包
    path('mywallet/settings', views.set_my_wallet, name='set_my_wallet'),
]
