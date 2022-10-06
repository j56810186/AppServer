
from django.urls import path

import market.views as views


urlpatterns = [
    # 二手拍賣頁面
    path('my-products/', views.get_my_products, name='my_products'),
    path('my-products/create/<int:clothePk>', views.PostCreateView.as_view(), name='my_product_create'),
    path('my-products/<int:pk>', views.get_my_single_product, name='my_product'),
    path('my-products/<int:pk>/edit', views.PostUpdateView.as_view(), name='my_product_update'),
    path('my-products/<int:pk>/delete', views.PostDeleteView.as_view(), name='my_product_delete'),


    path('secondhand', views.list_goods, name='products'),
    path('secondhand/<int:pk>', views.get_secondhand_post, name='product'),
    path('secondhand/<int:pk>/comments', views.get_secondhand_comments, name='product_comments'),


    # 購物車
    path('cart', views.CartListView.as_view(), name='carts'),
    path('cart/<int:pk>', views.CartDetailView.as_view(), name='cart'),
    path('cart/<int:pk>/delete', views.CartDeleteView.as_view(), name='cart_delete'),
    path('cart/create', views.CartCreateView.as_view(), name='cart_create'),
    path('cart/trasaction', views.CartToTransactionView.as_view(), name='cart_to_transaction'),
    path('transactionlog', views.get_transaction_log, name='transactionlog_list'), # 交易紀錄
    path('mywallet', views.get_my_wallet, name='my_wallet'), # 錢包
    path('mywallet/settings', views.set_my_wallet, name='set_my_wallet'),
]
