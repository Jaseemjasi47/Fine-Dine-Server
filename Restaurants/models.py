from django.db import models
from accounts.models import User
from django.db.models import UniqueConstraint



class Restaurant(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='resimages/', blank=True, null=True)
    description = models.TextField()
    place = models.CharField(max_length=100, null=True)
    license = models.FileField(upload_to='licenses/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants_owned')
    created_date = models.DateTimeField(auto_now_add=True)
    ratings = models.DecimalField(max_digits=3, decimal_places=1, default=0)

    def __str__(self):
        return self.name

    

class Food(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='food_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(max_length=450, null=True)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    def __str__(self):
        return self.name


class Table(models.Model):
    table_number = models.CharField(max_length=50)
    seat_capacity = models.PositiveIntegerField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Table {self.table_number} at {self.restaurant}"

    # class Meta:
    #     # Create a unique constraint on table_number and restaurant fields
    #     # to ensure uniqueness within each restaurant
    #     constraints = [
    #         UniqueConstraint(fields=['table_number', 'restaurant'], name='unique_table_number_per_restaurant')
    #     ]

# class Reservation(models.Model):
#     STATUS_CHOICES = (
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#         ('cancelled', 'Cancelled'),
#     )
#     PAYMENT_CHOICES = (
#         ('pending', 'Pending'),
#         ('paid', 'Paid'),
#         ('cancelled', 'Cancelled'),
#     )

#     restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     time_slot = models.TimeField()
#     table_no = models.ForeignKey(Table, on_delete=models.CASCADE)
#     persons = models.PositiveIntegerField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pending')

#     class Meta:
#         # Add a unique constraint to ensure there is no overlapping reservation for a table at the same date and time
#         unique_together = ('table_no', 'date', 'time_slot')

#     def __str__(self):
#         return f"{self.user.name}'s reservation at {self.restaurant.name} on {self.date} - {self.time_slot}"
    
    

# class PreOrderFood(models.Model):
#     reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
#     food = models.ForeignKey(Food, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()

#     def __str__(self):
#         return f"{self.quantity} x {self.food.name} for {self.reservation}"


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Declined', 'Declined'),
        ('Cancelled', 'Cancelled'),
    )
    PAYMENT_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    persons = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    totalAmount = models.PositiveIntegerField(blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.name}'s reservation at {self.restaurant.name}"
    

class ReservedTable(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE )
    table_no = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.TimeField()

    class Meta:
        # Add a unique constraint to ensure there is no overlapping reservation for a table at the same date and time
        unique_together = ('table_no', 'date', 'time_slot')

    def __str__(self):
        return f"{self.table_no.table_number} reserved on {self.date} - {self.time_slot}"


class PreOrderFood(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, blank=True, null=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    def __str__(self):
        return f"{self.quantity} x {self.food.name} for {self.reservation}"
