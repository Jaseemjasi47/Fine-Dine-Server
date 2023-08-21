from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Restaurant, Food, Table, ReservedTable, PreOrderFood, Reservation
from .serializers import RestaurantSerializer, TableSerializer, UserSerializer, FoodSerializer, ReservationSerializer, UserReservationSerializer,BookingSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from accounts.models import User
from django.db.models import Q
from datetime import datetime, timedelta
from .utilities import genarate_mail
from rest_framework.parsers import MultiPartParser


# -----------------------owner side------------------

class RestaurantBookingAPIView(APIView):

    permission_classes = [IsAuthenticated]  

    def get(self, request, restaurant_id, format=None):
        try:
            
            reservations = Reservation.objects.filter(restaurant_id=restaurant_id)
            serializer = UserReservationSerializer(reservations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Reservation.DoesNotExist:
            return Response({"detail": "Reservations not found for the given restaurant."}, status=status.HTTP_404_NOT_FOUND)

import json

class UpdateRestaurantView(APIView):
    parser_classes = (MultiPartParser,)

    def patch(self, request, restaurant_id):
        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'restaurant_image' in request.FILES:
            restaurant.image = request.FILES['restaurant_image']
            restaurant.save()

        restaurant_data = json.loads(request.data['restaurant'])  # Deserialize JSON string to dictionary
        restaurant_data.pop('image', None)
        
        

        # Update restaurant details
        restaurant_serializer = RestaurantSerializer(
            restaurant,
            data=restaurant_data,
            partial=True
        )
        if restaurant_serializer.is_valid():
            restaurant_serializer.save()
        else:
            print('Restaurant serializer errors:', restaurant_serializer.errors)

        # Update restaurant image (if provided)
        
        print(request.data,'[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]')
        foods_data = request.data.getlist('foods[]')  # Get a list of all foods data
        print(foods_data,'=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
        for food_data in foods_data:
            try:
                food_data_dict = json.loads(food_data)  # Deserialize food data JSON
                food = Food.objects.get(pk=food_data_dict['id'])
                print(food_data_dict,'fffffffffffffffffffffffffffffffffff')
            except (Food.DoesNotExist, KeyError):
                print('not working....................')
                continue

            food_serializer = FoodSerializer(
                food,
                data=food_data_dict,
                partial=True
            )
            if food_serializer.is_valid():
                food_serializer.save()
            else:
                print('Food serializer errors:', food_serializer.errors)

            # Update food image (if provided)
            # food_image_key = f'food_image_{food.id}'
            # if food_image_key in request.FILES:
            #     food.image = request.FILES[food_image_key]
            #     food.save()

        return Response({'message': 'Restaurant and food details updated successfully'})

        # return Response(status=status.HTTP_400_BAD_REQUEST)


class ReservationStatusUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        reservation_id = request.data.get('reservation_id')
        new_status = request.data.get('new_status')

        try:
            reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)

        if new_status not in dict(Reservation.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        reservation.status = new_status
        reservation.save()

        return Response({"message": "Reservation status updated successfully"}, status=status.HTTP_200_OK)
    


class CreateFoodView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data,'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
        serializer = FoodSerializer(data=request.data)

        if serializer.is_valid():
            # Get the restaurant ID from the request data
            restaurant_id = request.data.get("restaurant")

            # Perform any additional validation or manipulation here if needed

            # Create a new Food instance with the restaurant ID
            food = Food.objects.create(restaurant_id=restaurant_id, **serializer.validated_data)

            return Response(FoodSerializer(food).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteFoodView(APIView):
    def delete(self, request, id):
        try:
            food = Food.objects.get(pk=id)
        except Food.DoesNotExist:
            return Response({'error': 'Food not found'}, status=status.HTTP_404_NOT_FOUND)

        food.delete()
        return Response({"message": "Food Deleted successfully"}, status=status.HTTP_200_OK)

# -----------------------owner side end-------------------


class RestaurantCreateView(APIView):
    def post(self, request, format=None):
        # Check if the owner user exists based on the provided email
        owner_email = request.data.get('email')
        try:
            owner = User.objects.get(email=owner_email)
        except User.DoesNotExist:
            # Return 400 Bad Request with an error message
            return Response({'error': f'User with email {owner_email} not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the owner field to the authenticated user
        request.data['owner'] = owner.pk

        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            # Save the restaurant
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






# -----------------------------admin side-----------------------------



class RestaurantListView(APIView):

    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        restaurants = Restaurant.objects.all().order_by('-ratings')
        serializer = RestaurantSerializer(restaurants, many=True)
        
        # Fetch the User data for the approved_by field and serialize it
        user_ids = [restaurant['approved_by'] for restaurant in serializer.data if restaurant['approved_by']]
        User = get_user_model()
        users = User.objects.filter(id__in=user_ids)
        user_serializer = UserSerializer(users, many=True)
        user_mapping = {user.id: user_serializer.data[i] for i, user in enumerate(users)}

        # Update the approved_by field in the serializer.data with the serialized User data
        for restaurant in serializer.data:
            approved_by_id = restaurant.get('approved_by')
            if approved_by_id:
                restaurant['approved_by'] = user_mapping[approved_by_id]

        return Response(serializer.data)
    

class UserListView(APIView):
    def get(self, request):
        users = User.objects.all().order_by('id')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class ChangeRestaurantStatus(APIView):
    def patch(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')  # Get new status from request data
        approved_by_email = request.data.get('approved_by')  # Get user ID from request data

        # Update restaurant status and approved_by field
        restaurant.status = new_status
        if new_status == 'Approved':
            try:
                user = User.objects.get(email=approved_by_email)
                restaurant.approved_by = user
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            restaurant.approved_by = None

        restaurant.save()

        if restaurant.owner.email:
            genarate_mail(restaurant.owner.email, restaurant.owner.name, new_status)

        return Response({'message': 'Restaurant status updated successfully'}, status=status.HTTP_200_OK)


# ------------------------------admin side end -----------------------------

class TopRatedRestaurants(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        top_rated_restaurants = Restaurant.objects.filter(ratings__gt=0).order_by('-ratings')[:10]
        serializer = RestaurantSerializer(top_rated_restaurants, many=True)
        return Response(serializer.data)
    

class RestaurantDetail(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        restaurant_id = request.GET.get('id', '')
        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data)
        except Restaurant.DoesNotExist:
            return JsonResponse({'error': 'Restaurant not found'}, status=404)
    

class RestaurantFoods(APIView):
    permission_classes = [AllowAny]

    def get(self, request, restaurant_id):
        try:
            foods = Food.objects.filter(restaurant_id=restaurant_id)
            data = [
                {
                    'id': food.id,
                    'name': food.name,
                    'image': food.image.url if food.image else None,
                    'price': food.price,
                    'description': food.description,
                }
                for food in foods
            ]
            return JsonResponse(data, safe=False)
        except Restaurant.DoesNotExist:
            return JsonResponse({'error': 'Restaurant not found'}, status=404)
        


@api_view(['GET'])
def get_available_restaurants(request):
    name = request.GET.get('name', '')
    place = request.GET.get('place', '')

    # Filter the Restaurant model based on the provided parameters
    if place.strip():
        filtered_restaurants = Restaurant.objects.filter(name__icontains=name, place__icontains=place).order_by('-ratings')
    else:
        filtered_restaurants = Restaurant.objects.filter(name__icontains=name).order_by('-ratings')

    serializer = RestaurantSerializer(filtered_restaurants, many=True)
    return Response(serializer.data)



# class RestaurantTablesAPIView(APIView):
#     def get(self, request, restaurant_id):
#         try:
#             # Fetch the provided date and time from the request query parameters
#             date = request.query_params.get('date')
#             time_str = request.query_params.get('time')
#             time = datetime.strptime(time_str, '%H:%M').time()

#             # Calculate 1 hour before and after the given time
#             one_hour_before = (datetime.combine(datetime.min, time) - timedelta(minutes=59)).time()
#             one_hour_after = (datetime.combine(datetime.min, time) + timedelta(minutes=59)).time()

#             # Fetch the tables for the specified restaurant
#             tables = Table.objects.filter(restaurant__id=restaurant_id)
#             print(date, time, '*************************************')

#             # Check table availability for the provided date and time range
#             available_tables = []
#             for table in tables:
#                 is_available = not Reservation.objects.filter(
#                     Q(table_no=table) &
#                     Q(date=date) &
#                     Q(time_slot__gte=one_hour_before, time_slot__lte=one_hour_after)
#                 ).exists()
#                 available_tables.append({
#                     'table_id': table.id,
#                     'table_number': table.table_number,
#                     'seat_capacity': table.seat_capacity,
#                     'is_available': is_available,
#                 })
#             print(available_tables, '++++++++++++++++++++++++++++  available_tables +++++++++++++++++')
#             return Response(available_tables, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': 'Error fetching tables data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantTablesAPIView(APIView):
    def get(self, request, restaurant_id):
        try:
            # Fetch the provided date and time from the request query parameters
            date = request.query_params.get('date')
            time_str = request.query_params.get('time')
            time = datetime.strptime(time_str, '%H:%M').time()

            # Calculate 1 hour before and after the given time
            one_hour_before = (datetime.combine(datetime.min, time) - timedelta(minutes=59)).time()
            one_hour_after = (datetime.combine(datetime.min, time) + timedelta(minutes=59)).time()

            # Fetch the tables for the specified restaurant
            tables = Table.objects.filter(restaurant__id=restaurant_id)

            # Check table availability for the provided date and time range
            available_tables = []
            for table in tables:
                is_available = not ReservedTable.objects.filter(
                    Q(table_no=table) &
                    Q(date=date) &
                    Q(time_slot__gte=one_hour_before, time_slot__lte=one_hour_after)
                ).exists()
                available_tables.append({
                    'table_id': table.id,
                    'table_number': table.table_number,
                    'seat_capacity': table.seat_capacity,
                    'is_available': is_available,
                })

            return Response(available_tables, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Error fetching tables data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------------------------Booking-----------------


class ReservationCreateAPIView(APIView):
    def post(self, request):
        try:
            # Assuming the request data contains the required fields for the reservation
            serializer = ReservationSerializer(data=request.data)

            if serializer.is_valid():
                # Save the reservation
                reservation = serializer.save()

                # Assuming the request data contains an array of reserved_tables with table_no, date, and time_slot fields
                for table_data in request.data.get('reserved_tables', []):
                    reserved_table = ReservedTable.objects.create(
                        reservation=reservation,
                        table_no_id=table_data.get('table_no'),
                        date=table_data.get('date'),
                        time_slot=table_data.get('time_slot'),
                    )

                    # Check if pre-booked foods are provided in the request
                    pre_booked_foods = table_data.get('pre_booked_foods')
                    if pre_booked_foods:
                        for food_data in pre_booked_foods:
                            PreOrderFood.objects.create(
                                reserved_table=reserved_table,
                                food_id=food_data.get('food_id'),
                                quantity=food_data.get('quantity'),
                            )

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error creating reservation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------------------booking section end-------------------------------


class Foods(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        foods = Food.objects.all().order_by('-ratings')
        serializer = FoodSerializer(foods, many=True)
        return Response(serializer.data)
        
class UserRestaurants(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, user_email):
        user = User.objects.get(email=user_email)
        restaurants = Restaurant.objects.filter(owner=user)
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    
class GetTablesDataView(APIView):
    def post(self, request, format=None):
        table_ids = request.data.get('tableIds', [])
        table_data = Table.objects.filter(id__in=table_ids).values()
        return Response(table_data, status=status.HTTP_200_OK)
    
from django.utils import timezone

class UserReservationView(APIView):
    def get(self, request, *args, **kwargs):
        user_email = request.GET.get('email', None)
        if user_email is None:
            return Response({'error': 'User email not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_reservations = Reservation.objects.filter(user__email=user_email).order_by('-id')

            for reservation in user_reservations:
                if reservation.reservedtable_set.filter(date__lt=timezone.now().date()).exists():
                    reservation.status = 'completed'
                    reservation.save()

            serialized_reservations = serialize_user_reservations(user_reservations)
            return Response(serialized_reservations, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def serialize_user_reservations(reservations):
    serializer = UserReservationSerializer(reservations, many=True)
    serialized_data = serializer.data
    return serialized_data



# ---------------------booking--------------------------

class CreateReservation(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            print(data,'----------------------data-----------')
            # Extract data from the request
            selected_tables = data.get('selectedTable')
            selected_date = data.get('selectedDate')
            selected_time = data.get('selectedTime')
            selected_foods = data.get('selectedFoodData')
            useremail =  data.get('user') # Assuming the user is authenticated
            # print(useremail['email'],'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            user = User.objects.get(email=useremail['email'])
            print(selected_tables[0]['id'],'============================')
            # Create a new reservation
            reservation = Reservation.objects.create(
                restaurant_id=selected_tables[0]['restaurant_id'],  # Assign the ID directly
                user_id=user.id,  # Use the user object
                persons = 0,
                status='pending',  # You can set an appropriate status here
                payment_status='pending',  # You can set an appropriate payment status here
                totalAmount = data.get('totalAmount')
            )

            print('heloooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')  
            # Create ReservedTable instances
            for table_id in selected_tables:
                ReservedTable.objects.create(
                    reservation=reservation,
                    table_no_id=table_id['id'],
                    date=selected_date,
                    time_slot=selected_time,
                )
            print('[[[[[[[[[[[[[[[[[tablesss]]]]]]]]]]]]]]]]]')
            # Create PreOrderFood instances
            for food_data in selected_foods:
                PreOrderFood.objects.create(
                    reservation=reservation,
                    food_id=food_data['foodId'],
                    quantity=food_data['quantity'],
                    price=0,  # You need to calculate the actual price here
                )


            return Response({'message': 'Reservation created successfully', 'id': reservation.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'message': 'An error occurred', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



# ------------------------------------payment section(stripe)---------------------------------



from django.conf import settings
import stripe
from django.shortcuts import redirect

stripe.api_key=settings.STRIPE_SECRET_KEY

API_URL="http://locahost:8000/"


class CreateCheckOutSession(APIView):
    print('started paymen')
    def post(self, request, *args, **kwargs):
        # Reservation_id=id
        # print(Reservation_id,'---------id got')
        total_amount = int(request.data.get('totalAmount')) * 100
        id = int(request.data.get('id'))
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price_data': {
                            'currency':'inr',
                             'unit_amount':total_amount,
                             'product_data':{
                                 'name':'Thanks To Choose FineDine',
                                 
                             }
                        },
                        'quantity': 1,
                    },
                ],
                # metadata={
                #     "product_id":Reservation.id
                # },
                mode='payment',
                success_url=settings.SITE_URL + '/profile',
                cancel_url=settings.SITE_URL + '/',
            )


            reservation = Reservation.objects.get(id=id)

            # Update the payment_status if the checkout is successful
            reservation.payment_status = 'paid'
            reservation.save()
            print(Response)
            print(checkout_session,'---------session')
            print('before redirection')
            return redirect(checkout_session.url)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'msg': 'something went wrong while creating stripe session', 'error': str(e)}, status=500)
        

# --------------------------------------payment section end--------------------------------

class CancelReservation(APIView):
    def patch(self, request, id):
        try:
            reservation = Reservation.objects.get(pk=id)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)
        reservation.status = 'Cancelled'
        reservation.save()
        return Response({'Message': 'Reservation Canceled Successfully'}, status=status.HTTP_200_OK)