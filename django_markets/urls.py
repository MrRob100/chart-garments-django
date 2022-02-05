"""django_markets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from market_data import views as md_views
from printify import views as p_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stock/<str:symbol>', md_views.stock_candles, name='stock_candles'),
    path('crypto/<str:symbol>', md_views.crypto_candles, name='crypto_candles'),
    path('forex/<str:pair>', md_views.forex_candles, name='forex_candles'),
    path('symbols/crypto', md_views.crypto_symbols, name='crypto_symbols'),
    path('products/create', p_views.create_product, name='create_product'),
]
