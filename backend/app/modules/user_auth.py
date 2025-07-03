import datetime
from datetime import date, timedelta
import time
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import UserProfile, UserAchievements

@api_view(['POST'])
def login(request):
    '''Function for user login'''
    if request.method == 'POST':
        data = request.data
        email = data["email"]
        password = data["password"]
        has_user_profile = False

        try:
            user = User.objects.get(email=email)
        except:
            return JsonResponse({'error': "No user with this email"}, status=400)

        if user.is_active == False:
            return JsonResponse({'error': 'User not active.'}, status=400)

        user_password = user.password
        if check_password(password, user_password):
            refresh = RefreshToken.for_user(user)

            try:
                UserProfile.objects.get(User=user)
                has_user_profile = True
            except:
                pass

            return JsonResponse({'message': 'Login succesfully.',
                                'access_token': str(refresh.access_token),
                                 'refresh_token': str(refresh),
                                 'has_user_profile': has_user_profile}, status=200)
        else:
            return JsonResponse({'error': 'Wrong credentials.'}, status=400)


@api_view(['POST'])
def register(request):
    '''Fucntion for user registration'''

    # Check the request method.
    if request.method != 'POST':
        return JsonResponse({"error": "No POST request."}, status=400)

    data = request.data
    username = data["username"]
    email = data["email"]
    password = data["password"]
    # confirm_password = data["confirmPassword"]
    username = data["username"]

    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': "Email already exist"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': "Username already exist"}, status=400)

    # Create the user
    user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
    refresh = RefreshToken.for_user(user)

    try:
        signer = TimestampSigner()
        expiration_hours = 24
        expiration_timestamp = int((datetime.datetime.now() + timedelta(hours=expiration_hours)).timestamp())
        token = signer.sign(f'{refresh}:{expiration_timestamp}')

        email_context = {
            'username': user.username,
            'activation_link': f'https://www.planeat-app.ovh/pages/activation/accountActivationPage/{token}',
            'support_email': 'planeat_project@iti.gr',  # Replace with your support email
        }
        email_body = render_to_string('../templates/activationEmail.html', email_context)

        # Your email sending logic here
        email = EmailMessage(
            'Activate Your Account',
            email_body,
            settings.EMAIL_HOST_USER,
            [user.email]
        )

        email.fail_silently=False
        email.send()

        UserAchievements.objects.create(
            user=user,
            points=0,
            badges=[],
            trails=[],
            level=1
        )
    except ImportError:
        return JsonResponse({'error': "Email was not send"}, status=400)

    return JsonResponse({'message': 'User registered successfully',
                            'access_token': str(refresh.access_token),
                            'refresh_token': str(refresh)}, status=200)


@api_view(['POST'])
def reset_password(request, token):
    # Check the request method.
    if request.method != 'POST':
        return JsonResponse({"error": "No POST request."}, status=400)

    signer = TimestampSigner()
    password = request.data["password"]

    try:
        # Verify and extract the username and expiration timestamp from the token
        refresh_token, expiration_timestamp = signer.unsign(token).split(':')
        refresh = RefreshToken(refresh_token)
        user_id = refresh.payload.get('user_id')

        # Convert the expiration timestamp to a datetime object
        expiration_datetime = datetime.datetime.fromtimestamp(int(expiration_timestamp))
        #print(expiration_datetime)

        # Check if the token has expired
        if datetime.datetime.now() <= expiration_datetime:
            user = User.objects.get(id = user_id)
            password = make_password(password)
            user.password = password
            user.save()
            return JsonResponse("successful change password", status=200, safe=False)

            # try:
            #     validate_password(password)
            #     validate_password(password2)
            #     if password == password2:
            #         password = make_password(password)
            #         user.password = password
            #         user.save()
            #         return JsonResponse("successful change password", safe=False)
            #     else:
            #         return JsonResponse({'error': "Passowrd and comfirm password do not match"}, status=400)
            # except:
            #     return JsonResponse({'error': "Invalid password. Please check for the password validations"}, status=400)
        else:
            return JsonResponse("Activation link has expired.", status=400, safe=False)

    except SignatureExpired:
        return JsonResponse("Activation link has expired.", status=400, safe=False)
    except BadSignature:
        return JsonResponse("Invalid activation link.", status=400, safe=False)


@api_view(['POST'])
def reset_password_email(request, email):
    # Check the request method.
    if request.method != 'POST':
        return JsonResponse({"error": "No POST request."}, status=400)
    try:
        user = User.objects.get(email= email)
        try:
            refresh = RefreshToken.for_user(user)
            refresh['is_active'] = user.is_active

            signer = TimestampSigner()
            expiration_hours = 24
            expiration_timestamp = int((datetime.datetime.now() + timedelta(hours=expiration_hours)).timestamp())
            token = signer.sign(f'{refresh}:{expiration_timestamp}')

            email_context = {
                'username': user.username,
                'resetpassword_link': f'https://www.planeat-app.ovh/pages/password/resetPasswordPage/{token}',
                #'resetpassword_link': f'http://195.251.117.84:4000/resetpassword/{token}',
                'support_email': 'planeat_project@iti.gr',  # Replace with your support email
            }
            email_body = render_to_string('../templates/resetPasswordEmail.html', email_context)
            # Your email sending logic here
            email = EmailMessage(
                'Activate Your Account',
                email_body,
                settings.EMAIL_HOST_USER,
                [user.email]
            )
            email.fail_silently=False
            email.send()

            return JsonResponse("Email send successfully", safe=False)
        except :
            return JsonResponse({'error': "Email was not send"}, status=400)
    except:
        return JsonResponse({'error': "No active account matches this email address"}, status=400)


@api_view(['POST'])
def activate(request, token):
    # Check the request method.
    if request.method != 'POST':
        return JsonResponse({"error": "No POST request."}, status=400)
    signer = TimestampSigner()
    try:
        # Verify and extract the username and expiration timestamp from the token
        refresh_token, expiration_timestamp = signer.unsign(token).split(':')
        refresh = RefreshToken(refresh_token)
        user_id = refresh.payload.get('user_id')

        # Convert the expiration timestamp to a datetime object
        expiration_datetime = datetime.datetime.fromtimestamp(int(expiration_timestamp))
        #print(expiration_datetime)

        # Check if the token has not expired
        if datetime.datetime.now() <= expiration_datetime:
            user = User.objects.get(id = user_id)
            user.is_active = True
            user.save()
            return JsonResponse("Activation successful", safe=False)
        else:
            return JsonResponse({'error': "Activation link has expired 1."}, status=400, safe=False)
    except SignatureExpired:
        return JsonResponse({'error': "Activation link has expired 2."}, status=400)
    except BadSignature:
        return JsonResponse({'error': "Invalid activation link 3."}, status=400)


@api_view(['POST'])
def activation_email(request, email):
    # Check the request method.
    if request.method != 'POST':
        return JsonResponse({"error": "No POST request."}, status=400)
    try:
        user = User.objects.get(email= email)
        try:
            signer = TimestampSigner()
            expiration_hours = 24
            expiration_timestamp = int((datetime.datetime.now() + timedelta(hours=expiration_hours)).timestamp())
            token = signer.sign(f'{refresh}:{expiration_timestamp}')

            email_context = {
                'username': user.username,
                'activation_link': f'https://www.planeat-app.ovh/pages/activation/accountActivationPage/{token}',
                'support_email': 'planeat_project@iti.gr',  # Replace with your support email
            }
            email_body = render_to_string('../templates/activationEmail.html', email_context)

            # Your email sending logic here
            email = EmailMessage(
                'Activate Your Account',
                email_body,
                settings.EMAIL_HOST_USER,
                [user.email]
            )

            email.fail_silently=False
            email.send()
            return JsonResponse("Email send successfully", safe=False)
        except :
            return JsonResponse({'error': "Email was not send"}, status=400)
    except:
        return JsonResponse({'error': "No account matches this email address"}, status=400)
