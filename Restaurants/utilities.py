from django.core.mail import send_mail



def genarate_mail(email,name,status):
    # Send OTP via email
    send_mail(
        'Restaurant Verification Details',
        f'Hai {name}, Welcome To FineDine Your Restaurant is {status}',
        'sender@example.com',
        [email],  # Use user.email instead of undefined email variable
        fail_silently=False,
        )
    return 