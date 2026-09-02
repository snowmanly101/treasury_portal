import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Transaction, UserProfile


def home_view(request):
  return redirect('debit_cards')


def login_view(request):
  error_message = None
  warning_message = None

  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')

    attempts = request.session.get('failed_attempts', 0)

    if attempts >= 5:
      error_message = (
          'Your account has been locked due to multiple failed security'
          ' attempts. Please contact the bank to unlock.'
      )
      return render(request, 'main/login.html', {'error': error_message})

    # --- LOCATION DETECTION (IP Geolocation) ---
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
      ip = x_forwarded_for.split(',')[0]
    else:
      ip = request.META.get('REMOTE_ADDR')

    if ip in ['127.0.0.1', 'localhost', '::1']:
      country_code = 'US'
    else:
      try:
        geo_response = requests.get(
            f'https://ipapi.co/{ip}/json/', timeout=3
        ).json()
        country_code = geo_response.get('country_code', 'US')
      except:
        country_code = 'US'

    if country_code != 'US':
      request.session['account_banned'] = True
      return render(
          request,
          'main/login.html',
          {
              'error': (
                  'Access Denied: Unusual login location detected outside the'
                  ' USA. Your account has been restricted. Please contact the'
                  ' bank immediately.'
              )
          },
      )

    # --- AUTHENTICATION CHECK ---
    user = authenticate(request, username=username, password=password)

    if user is not None:
      # Log the user into the official Django session so request.user works properly
      login(request, user)
      request.session['failed_attempts'] = 0
      request.session['pre_auth_user_id'] = user.id
      return redirect('security_question')
    else:
      attempts += 1
      request.session['failed_attempts'] = attempts
      remaining = 5 - attempts

      if attempts >= 5:
        error_message = (
            'Security Alert: 5 incorrect password attempts reached. Account'
            ' temporarily locked. Please contact the bank to unlock.'
        )
      else:
        warning_message = (
            f'Invalid credentials. Warning: {remaining} attempt(s) remaining'
            ' before temporary account lock.'
        )

      return render(
          request,
          'main/login.html',
          {'error': error_message, 'warning': warning_message},
      )

  return render(request, 'main/login.html')


def security_question_view(request):
  if not request.session.get('pre_auth_user_id'):
    return redirect('login')

  error_message = None
  if request.method == 'POST':
    answer = request.POST.get('security_answer')
    request.session['pending_auth'] = True
    del request.session['pre_auth_user_id']
    return redirect('loading_auth')

  return render(request, 'main/security_question.html', {'error': error_message})


def signup_view(request):
  return render(request, 'main/signup.html')


def loading_auth_view(request):
  if not request.session.get('pending_auth'):
    return redirect('login')
  return render(request, 'main/loading_auth.html')


def verify_otp_view(request):
  if not request.session.get('pending_auth'):
    return redirect('login')

  if request.method == 'POST':
    entered_otp = request.POST.get('otp')
    PERMANENT_OTP = '7788'

    if entered_otp == PERMANENT_OTP:
      request.session['logged_in'] = True
      del request.session['pending_auth']
      return redirect('dashboard')
    else:
      return render(
          request,
          'main/verify_otp.html',
          {'error': 'Invalid Secure Authentication PIN'},
      )

  return render(request, 'main/verify_otp.html')


def dashboard_view(request):
  if not request.session.get('logged_in') and not request.user.is_authenticated:
    return redirect('login')

  try:
    if request.user.is_authenticated:
      # Strictly match the profile and transactions to the currently logged-in user
      profile = UserProfile.objects.filter(user=request.user).first()
      if profile:
        user_transactions = Transaction.objects.filter(user_profile=profile).order_by('-id')
      else:
        user_transactions = Transaction.objects.filter(user=request.user).order_by('-id')
        
      masked_email = request.user.email if request.user.email else 'user@treasury-estonia.ee'
      username_lower = request.user.username.lower()
    else:
      profile = None
      user_transactions = []
      masked_email = 'user@treasury-estonia.ee'
      username_lower = ''

    account_number = profile.account_number if profile else '••••4092'
    routing_number = profile.routing_id if profile else '8810'
    balance = profile.balance if profile else '0.00'
    status = 'Dormant (Strictly Restricted)' if (profile and profile.is_locked) else 'Active Profile'
  except Exception:
    account_number = '••••4092'
    routing_number = '8810'
    balance = '0.00'
    status = 'Active Profile'
    user_transactions = []
    masked_email = 'user@treasury-estonia.ee'
    username_lower = ''

  owner_name = request.user.get_full_name() if (request.user.is_authenticated and request.user.get_full_name()) else request.user.username

  context = {
      'owner_name': owner_name,
      'balance': balance,
      'currency': 'USD',
      'status': status,
      'institution': 'Classified Federal Treasury, Estonia',
      'account_number': account_number,
      'routing_number': routing_number,
      'swift_code': 'XXXX',
      'masked_email': masked_email,
      'masked_phone': '••••••••4092',
      'transactions': user_transactions,
  }

  return render(request, 'main/dashboard.html', context)


def add_external_account_view(request):
  if not request.session.get('logged_in') and not request.user.is_authenticated:
    return redirect('login')
  return render(request, 'main/add_external_account.html')


def contact_view(request):
  return render(request, 'main/contact.html')


def debit_cards_view(request):
  return render(request, 'main/debit_cards.html')


def logout_view(request):
  request.session.flush()
  return redirect('login')