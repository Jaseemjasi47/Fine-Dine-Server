from django.contrib import admin
from .models import Restaurant, Food, Table, Reservation, ReservedTable, PreOrderFood

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(Food)
admin.site.register(Table)
admin.site.register(Reservation)
admin.site.register(ReservedTable)
admin.site.register(PreOrderFood)