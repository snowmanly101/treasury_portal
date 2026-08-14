import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

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
            error_message = "Your account has been locked due to multiple failed security attempts. Please contact the bank to unlock."
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
                geo_response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3).json()
                country_code = geo_response.get('country_code', 'US')
            except:
                country_code = 'US'

        if country_code != 'US':
            request.session['account_banned'] = True
            return render(request, 'main/login.html', {
                'error': "Access Denied: Unusual login location detected outside the USA. Your account has been restricted. Please contact the bank immediately."
            })

        # --- AUTHENTICATION CHECK ---
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            request.session['failed_attempts'] = 0
            # Instead of logging in instantly, trigger the security loading/OTP flow
            request.session['pending_auth'] = True
            return redirect('loading_auth')
        else:
            attempts += 1
            request.session['failed_attempts'] = attempts
            remaining = 5 - attempts

            if attempts >= 5:
                error_message = "Security Alert: 5 incorrect password attempts reached. Account temporarily locked. Please contact the bank to unlock."
            else:
                warning_message = f"Invalid credentials. Warning: {remaining} attempt(s) remaining before temporary account lock."
                
            return render(request, 'main/login.html', {
                'error': error_message,
                'warning': warning_message
            })

    return render(request, 'main/login.html')

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
            # Authenticate fully and clear pending auth flag
            # Note: We can pull the user since login passed earlier, or re-verify
            request.session['logged_in'] = True
            del request.session['pending_auth']
            return redirect('dashboard')
        else:
            return render(request, 'main/verify_otp.html', {'error': 'Invalid Secure Authentication PIN'})
            
    return render(request, 'main/verify_otp.html')

def dashboard_view(request):
    if not request.session.get('logged_in') and not request.user.is_authenticated:
        return redirect('login')
    
    transactions = [
        {"date": "2025-11-12", "ref": "TXN-99412", "company": "****4902 - Barrick Gold Corp (Canada)", "amount": "+$185,400.00", "status": "Cleared"},
        {"date": "2023-04-19", "ref": "TXN-44102", "company": "****1184 - Deutsche bullion clearing (Germany)", "amount": "+$142,500.00", "status": "Cleared"},
        {"date": "2025-08-30", "ref": "TXN-88201", "company": "****7351 - Newmont Corporation (USA)", "amount": "+$198,200.00", "status": "Cleared"},
        {"date": "2022-02-14", "ref": "TXN-11930", "company": "****5529 - Zurich Reserve Desk (Switzerland)", "amount": "+$175,000.00", "status": "Cleared"},
        {"date": "2024-06-05", "ref": "TXN-66382", "company": "****9043 - Dubai Gold Bullion DMCC (UAE)", "amount": "+$160,300.00", "status": "Cleared"},
        {"date": "2023-12-01", "ref": "TXN-55219", "company": "****2267 - Kinross Gold Mining (Canada)", "amount": "+$130,500.00", "status": "Cleared"},
        {"date": "2022-09-18", "ref": "TXN-22485", "company": "****6810 - London Bullion Market Assoc (UK)", "amount": "+$115,000.00", "status": "Cleared"},
        {"date": "2024-10-22", "ref": "TXN-77391", "company": "****3156 - Singapore Mint & Depository (SG)", "amount": "+$155,000.00", "status": "Cleared"},
        {"date": "2023-07-08", "ref": "TXN-33820", "company": "****8492 - Evolution Mining Ltd (Australia)", "amount": "+$145,000.00", "status": "Cleared"},
        {"date": "2025-01-15", "ref": "TXN-88104", "company": "****5037 - Agnico Eagle Mines (Finland Desk)", "amount": "+$125,000.00", "status": "Cleared"},
        {"date": "2022-05-27", "ref": "TXN-10492", "company": "****1924 - Yamana Reserve Desk (Brazil)", "amount": "+$165,000.00", "status": "Cleared"},
        {"date": "2024-03-11", "ref": "TXN-61205", "company": "****7483 - Frankfurt Treasury Vault (Germany)", "amount": "+$198,000.00", "status": "Cleared"},
    ]
    
    context = {
        'owner_name': 'Daryl Tuchel Junior',
        'balance': '7,500,000.00',
        'currency': 'USD',
        'status': 'Dormant (Strictly Restricted)',
        'institution': 'Classified Federal Treasury, Estonia',
        'account_number': '••••••••1996',
        'routing_number': '725619978',
        'swift_code': 'XXXX',
        'masked_email': '••••••••@treasury-estonia.ee',
        'masked_phone': '••••••••9982',
        'transactions': transactions
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