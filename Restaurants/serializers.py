from rest_framework import serializers
from .models import Restaurant, Table, Food, Reservation, ReservedTable
from accounts.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email']

class RestaurantRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class RestaurantSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    class Meta:
        model = Restaurant
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email','is_admin','is_staff') 

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__' 


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'


# class ReservedTableSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ReservedTable
#         fields = '__all__'


class ReservedTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservedTable
        fields = ['date', 'time_slot', 'table_no']

class BookingSerializer(serializers.ModelSerializer):
    reserved_tables = ReservedTableSerializer(many=True, read_only=True)  # Include the related data
    print(reserved_tables,'99999999999999999999999999999999999999999')
    class Meta:
        model = Reservation
        fields = '__all__'


class UserReservationSerializer(serializers.ModelSerializer):
    restaurant_image = serializers.SerializerMethodField()
    tables = ReservedTableSerializer(source='reservedtable_set', many=True)
    user = user = UserSerializer()

    def get_restaurant_image(self, reservation):
        if reservation.restaurant.image:
            return reservation.restaurant.image.url,reservation.restaurant.name
        return None

    class Meta:
        model = Reservation
        fields = ['id', 'restaurant', 'restaurant_image', 'status', 'totalAmount', 'payment_status', 'tables', 'user']