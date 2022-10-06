
from django.urls import path

import market.views as views


urlpatterns = [
    # 二手拍賣頁面
    path('my-products/', views.get_my_products, name='my_products'),
    path('my-products/create/<int:clothePk>', views.PostCreateView.as_view(), name='my_product_create'),
    path('my-products/<int:pk>', views.get_my_product, name='my_product'),
    path('my-products/<int:pk>/edit', views.PostUpdateView.as_view(), name='my_product_update'),
    path('my-products/<int:pk>/delete', views.PostDeleteView.as_view(), name='my_product_delete'),


    path('products/', views.get_products, name='products'),
    path('products/<int:pk>', views.get_product, name='product'),
    path('products/<int:pk>/comments', views.get_product_comments, name='product_comments'),


    # 購物車
    path('cart', views.CartListView.as_view(), name='carts'),
    path('cart/create', views.CartCreateView.as_view(), name='cart_create'),
    path('cart/<int:pk>/delete', views.CartDeleteView.as_view(), name='cart_delete'),
    path('cart/trasaction', views.CartToTransactionView.as_view(), name='cart_to_transaction'),

    # transaction log.
    path('transactionlog', views.get_transaction_log, name='transaction_logs'),
    path('transactionlog/<int:pk>', views.get_single_transaction_log, name='transaction_log'),

    path('my-wallet', views.get_my_wallet, name='my_wallet'), # 錢包
    path('my-wallet/settings', views.set_my_wallet, name='set_my_wallet'),
]
