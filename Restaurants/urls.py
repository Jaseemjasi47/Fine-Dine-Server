from django.urls import path, include
from . import views


urlpatterns = [
    path('top_rated_restaurants/', views.TopRatedRestaurants.as_view(), name='top_rated_restaurants'),
    path('available_restaurants/', views.get_available_restaurants, name='available_restaurants'),
    path('restaurant_detail/', views.RestaurantDetail.as_view(), name='restaurant_detail'),
    path('restaurant_foods/<int:restaurant_id>/', views.RestaurantFoods.as_view(), name='restaurant-foods'),
    path('restaurants_tables/<int:restaurant_id>/', views.RestaurantTablesAPIView.as_view(), name='restaurant_tables'),
    path('restaurants/', views.RestaurantListView.as_view(), name='restaurant-list'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('topratedfoods/', views.Foods.as_view(), name='food-list'),
    path('user_restaurants/<str:user_email>/', views.UserRestaurants.as_view(), name='user-restaurants'),
    path('selectedtables/', views.GetTablesDataView.as_view(), name='get_tables_data'),
    path('createrestaurants/', views.RestaurantCreateView.as_view(), name='restaurant-create'),
    path('user_reservations/', views.UserReservationView.as_view(), name='user_reservations'),
    path('create-reservation/', views.CreateReservation.as_view(), name='create-reservation'),
    path('change-status/<int:pk>/', views.ChangeRestaurantStatus.as_view(), name='change-restaurant-status'),
    path('restaurants_bookings/<int:restaurant_id>/', views.RestaurantBookingAPIView.as_view(), name='restaurant-reservations'),
    path('payment/', views.CreateCheckOutSession.as_view(), name='change-restaurant-status'),
    path('cancel_reservations/<int:id>/', views.CancelReservation.as_view(), name='cancel-reservations'),
    path('update_restaurant/<int:restaurant_id>/', views.UpdateRestaurantView.as_view(), name='update-restaurant'),
    path('update_reservation_status/', views.ReservationStatusUpdateView.as_view(), name='update_reservation_status'),
    path('create-food/', views.CreateFoodView.as_view(), name='create-food'),
    path('delete-food/<int:id>/', views.DeleteFoodView.as_view(), name='delete-food'),

]