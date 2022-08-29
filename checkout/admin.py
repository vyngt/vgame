from django.contrib import admin
from .models import *


admin.site.register(OrderDetail)
admin.site.register(OrderItem)
admin.site.register(PaymentDetail)
