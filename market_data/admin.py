from django.contrib import admin
from .models import Candle
from .models import SymbolList

# Register your models here.

admin.site.register(Candle)
admin.site.register(SymbolList)