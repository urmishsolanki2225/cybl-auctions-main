from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.contrib.auth.models import User, Group
from adminpanel.models import *
from adminpanel.models.profile import Country, State, Profile
import random, string
from adminpanel.forms import EmailAuthenticationForm, SignUpForm, UserProfileForm, ForgotPasswordForm, CustomPasswordResetConfirmForm
from django.contrib.auth.views import PasswordResetConfirmView,PasswordResetCompleteView
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings  # Import settings
from django.core.cache import cache
from adminpanel.utils import get_coordinates_from_address


from django.contrib.admin.views.decorators import staff_member_required


#No Route then Redirect to Index
@login_required(login_url='login')
def redirect_login(request):
    return redirect('dashboard')

# Admin Login Page
def admin_login(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is None:
                form.add_error(None, "Please enter a correct username and password. Note that both fields may be case-sensitive.")
                return JsonResponse({'success': False, 'error': {'__all__': form.non_field_errors()[0]}})

            if user.groups.filter(name='Super Admin').exists():
                login(request, user)
                remember_me = request.POST.get('remember')  # Get the value of the 'remember' checkbox
                
                if remember_me:
                    request.session.set_expiry(1209600)  # Set session to expire in 2 weeks
                else:
                    request.session.set_expiry(0)  # Session will expire when the browser closes
                    
                # ✅ After successful login
                request.session['toast'] = {'type': 'success', 'message': 'Login successful. Welcome back!'}
                return JsonResponse({'success': True, 'redirect_url': '/superadmin/dashboard/'})
            else:
                return JsonResponse({'success': False, 'error': {'username': 'Only Super Admins can access this site'}})

        errors = {field: form.errors[field][0] for field in form.errors}
        return JsonResponse({'success': False, 'error': errors})

    return render(request, 'login.html', {'form': EmailAuthenticationForm()})

#Logout
def admin_logout(request):
    logout(request)
    return redirect('login')

# Index Page (After Login Page)
@login_required(login_url='login')
def dashboard(request):
    username = request.user.username
    toast = request.session.pop('toast', None)
    return render(request, 'dashboard.html', {'username': username, 'toast': toast})

# All Users
@login_required(login_url='login')
def all_users(request, tab_id):
    # Fetch users based on their group and order them by `created_at` (descending)
    buyers = User.objects.filter(groups__name='Buyer').order_by('-date_joined', 'username')
    sellers = User.objects.filter(groups__name='Seller').order_by('-date_joined', 'username')
    super_admins = User.objects.filter(groups__name='Super Admin').order_by('-date_joined', 'username')
    
    # Determine which tab to activate based on `tab_id`
    active_tab = 'buyers' if tab_id == 1 else 'sellers' if tab_id == 2 else 'super_admins'
    
    context = {
        'buyers': buyers,
        'sellers': sellers,
        'super_admins': super_admins,
        'active_tab': active_tab,
    }
    
    return render(request, 'users/index.html', context)

# Forgot Password Page
@csrf_exempt  # Use with caution; handle CSRF in production
def forget_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            UserModel = get_user_model()
            email = form.cleaned_data['email']
            users = UserModel.objects.filter(email=email)
            
            if users.exists():
                for user in users:
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_link = request.build_absolute_uri(reverse('password_reset_confirm', args=[uid, token]))
                    
                    subject = 'Password Reset Request'
                    message = render_to_string('password-reset-email-template.html', {
                        'email': user.email,
                        'fullname': user.first_name + ' ' + user.last_name,
                        'reset_link': reset_link,
                        'protocol': request.scheme,
                        'domain': request.get_host(),
                        'uid': uid,
                        'token': token,
                    })
                    return HttpResponse(message)
                    # Uncomment the next line to actually send the email
                    # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)
                    return JsonResponse({'success': True, 'message': 'Password reset email has been sent.'})
            return JsonResponse({'success': False, 'message': 'No user found with the provided email address.'})
        return JsonResponse({'success': False, 'errors': form.errors})
    # If the request method is GET, render the form
    form = ForgotPasswordForm()
    return render(request, 'forget-password.html', {'form': form})

#Create user
def generate_random_username():
    return 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@login_required(login_url='login')
def create_users(request):
    all_roles = Group.objects.all()
    countries = Country.objects.prefetch_related('states').all()
    
    if request.method == 'POST':
        random_username = generate_random_username()
        random_password = generate_random_password()

        request.POST = request.POST.copy()  # Make a mutable copy
        request.POST['username'] = random_username
        request.POST['password1'] = random_password
        request.POST['password2'] = random_password

        form = SignUpForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(random_password)
            user.save()
            form.save_m2m()  # Save many-to-many relationships

            print("Form cleaned_data:", form.cleaned_data)
            selected_group = form.cleaned_data['group']
            print(f"Selected group: {selected_group}")

            try:
                # Retrieve the Country and State instances for user profile
                country_instance = Country.objects.get(id=form.cleaned_data['country'])
                state_instance = State.objects.get(id=form.cleaned_data['state']) if form.cleaned_data['state'] else None
                
                # Initialize company variables
                company_instance = None
                company_country_instance = None
                company_state_instance = None
                
                if selected_group.id == 3 and form.cleaned_data.get('seller_type') == 'Company':
                    # Get company country and state instances if provided
                    if form.cleaned_data.get('company_country'):
                        company_country_instance = Country.objects.get(id=form.cleaned_data['company_country'])
                    if form.cleaned_data.get('company_state'):
                        company_state_instance = State.objects.get(id=form.cleaned_data['company_state'])
                    
                    # Get coordinates
                    zipcode = form.cleaned_data.get('company_zipcode')
                    lat, lng = get_coordinates_from_address(zipcode)

                    # Create the Company instance
                    company_instance = Company.objects.create(
                        name=form.cleaned_data['company_name'],
                        phone_no=form.cleaned_data['company_phone'],
                        address=form.cleaned_data['company_address'],
                        company_logo=form.cleaned_data.get('company_logo'),
                        country=company_country_instance,
                        state=company_state_instance,
                        city=form.cleaned_data.get('company_city'),
                        zipcode=form.cleaned_data.get('company_zipcode'),
                        latitude=lat,
                        longitude=lng
                    )
                    

                # Create or update the Profile instance
                profile, created = Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        'title': form.cleaned_data.get('title'),
                        'phone_no': form.cleaned_data.get('phone_no'),
                        'gender': form.cleaned_data.get('gender'),
                        'address': form.cleaned_data.get('address'),
                        'city': form.cleaned_data.get('city'),
                        'zipcode': form.cleaned_data.get('zipcode'),
                        'photo': form.cleaned_data.get('photo'),
                        'country': country_instance,
                        'state': state_instance,
                        'company': company_instance,
                        'seller_type': form.cleaned_data.get('seller_type'),
                    }
                )

                print("Profile created or updated:", profile)

                # Manage user groups
                print(f"User groups before assignment: {user.groups.all()}")
                user.groups.clear()
                user.groups.add(selected_group)
                user.save()  # Save to ensure group changes are committed
                print(f"User groups after assignment: {user.groups.all()}")

                # Verify the assigned group
                user.refresh_from_db()
                assigned_groups = user.groups.all()
                print(f"Assigned groups after refresh: {assigned_groups}")

                if selected_group not in assigned_groups:
                    return JsonResponse({'success': False, 'message': 'Group assignment failed.'})

                return JsonResponse({'success': True, 'message': 'User created successfully.'})
            except IntegrityError as e:
                return JsonResponse({'success': False, 'message': str(e)})
            except Country.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid country selected.'})
            except State.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid state selected.'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = SignUpForm()

    return render(request, 'users/create.html', {
        'form': form,
        'all_roles': all_roles,
        'countries': countries,
    })

# Edit Users
@login_required(login_url='login')
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    company = getattr(profile, 'company', None)  # Safely get company if it exists

    all_roles = Group.objects.all()
    countries = Country.objects.prefetch_related('states').all()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            try:
                # Update User instance
                user = form.save()

                # Update Profile instance
                profile_data = {
                    'title': form.cleaned_data.get('title'),
                    'phone_no': form.cleaned_data.get('phone_no'),
                    'gender': form.cleaned_data.get('gender'),
                    'address': form.cleaned_data.get('address'),
                    'city': form.cleaned_data.get('city'),
                    'zipcode': form.cleaned_data.get('zipcode'),
                    'seller_type': form.cleaned_data.get('seller_type'),
                    'country': Country.objects.get(id=form.cleaned_data['country']),
                    'state': State.objects.get(id=form.cleaned_data['state']) if form.cleaned_data['state'] else None,
                }
                
                if 'photo' in form.cleaned_data and form.cleaned_data['photo'] is not None:
                    profile_data['photo'] = form.cleaned_data['photo']

                # Update or create profile
                Profile.objects.update_or_create(
                    user=user,
                    defaults=profile_data
                )

                # Handle Company data if seller type is Company
                if form.cleaned_data.get('seller_type') == 'Company':
                    company_data = {
                        'name': form.cleaned_data['company_name'],
                        'phone_no': form.cleaned_data['company_phone'],
                        'address': form.cleaned_data['company_address'],
                        'country': Country.objects.get(id=form.cleaned_data['company_country']) if form.cleaned_data['company_country'] else None,
                        'state': State.objects.get(id=form.cleaned_data['company_state']) if form.cleaned_data['company_state'] else None,
                        'city': form.cleaned_data.get('company_city'),
                        'zipcode': form.cleaned_data.get('company_zipcode'),
                    }
                    
                    if 'company_logo' in form.cleaned_data and form.cleaned_data['company_logo'] is not None:
                        company_data['company_logo'] = form.cleaned_data['company_logo']

                    # Get coordinates
                    zipcode = company_data.get('zipcode')
                    lat, lng = get_coordinates_from_address(zipcode)
                    company_data['latitude'] = lat
                    company_data['longitude'] = lng

                    if company:
                        # Update existing company
                        for key, value in company_data.items():
                            if value is not None:  # Only update if value is provided
                                setattr(company, key, value)
                        company.save()
                    else:
                        # Create new company
                        company_data['profile'] = profile
                        Company.objects.create(**company_data)
                elif company:
                    # If seller type changed from Company to something else, delete the company
                    company.delete()

                # Manage user groups
                user.groups.clear()
                user.groups.add(form.cleaned_data['group'])

                return JsonResponse({'success': True, 'message': 'User updated successfully.'})

            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        # Prepare initial data for the form
        initial_data = {
            'title': profile.title,
            'phone_no': profile.phone_no,
            'gender': profile.gender,
            'address': profile.address,
            'city': profile.city,
            'zipcode': profile.zipcode,
            'photo': profile.photo,
            'country': profile.country.id if profile.country else None,
            'state': profile.state.id if profile.state else None,
            'group': user.groups.first(),
            'seller_type': profile.seller_type,
        }

        # Add company data if exists
        if company:
            initial_data.update({
                'company_name': company.name,
                'company_phone': company.phone_no,
                'company_address': company.address,
                'company_logo': company.company_logo,
                'company_country': company.country.id if company.country else None,
                'company_state': company.state.id if company.state else None,
                'company_city': company.city,
                'company_zipcode': company.zipcode,
            })

        form = UserProfileForm(initial=initial_data, instance=user)

    return render(request, 'users/edit.html', {
        'form': form,
        'user': user,
        'all_roles': all_roles,
        'countries': countries,
        'MEDIA_URL': settings.MEDIA_URL
    })

#Change Password
@csrf_exempt
@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        user = authenticate(username=request.user.username, password=old_password)
        
        if user is not None:
            request.user.set_password(new_password)
            request.user.save()
            logout(request)  
            
            return JsonResponse({
                'success': True, 
                'message': 'Your password has been changed successfully. You will be logged out shortly.'
            })
        else:
            return JsonResponse({'success': False, 'errors': {'old_password': ['Old password is incorrect.']}})

    return render(request, 'users/change-password.html')

# add for countries start
@login_required(login_url='login')
def fetch_states(request):
    country_id = request.GET.get('country_id')

    if not country_id:
        return JsonResponse({'error': 'No country_id provided'}, status=400)

    try:
        states = State.objects.filter(country_id=country_id).values('id', 'name')
        states_list = list(states)
        return JsonResponse({'states': states_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# add for countries end
@login_required(login_url='login')
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('userId')
        user = get_object_or_404(User, id=user_id)
        try:
            user.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required(login_url='login')
def my_profile(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    company = profile.company  # This assumes a one-to-one relationship with company

    all_roles = Group.objects.all()
    countries = Country.objects.prefetch_related('states').all()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Update Profile instance
            profile.title = form.cleaned_data.get('title')
            profile.phone_no = form.cleaned_data.get('phone_no')
            profile.gender = form.cleaned_data.get('gender')
            profile.address = form.cleaned_data.get('address')
            profile.city = form.cleaned_data.get('city')
            profile.zipcode = form.cleaned_data.get('zipcode')

            if 'photo' in request.FILES:
                if profile.photo:
                    if os.path.isfile(profile.photo.path):
                        os.remove(profile.photo.path)
                profile.photo = request.FILES['photo']
            elif request.POST.get('delete_photo') == 'true':
                if profile.photo:
                    if os.path.isfile(profile.photo.path):
                        os.remove(profile.photo.path)
                    profile.photo = None
                    
            profile.country = Country.objects.get(id=form.cleaned_data['country'])
            profile.state = State.objects.get(id=form.cleaned_data['state']) if form.cleaned_data['state'] else None
            profile.seller_type = form.cleaned_data.get('seller_type')
            profile.save()

            return JsonResponse({'success': True, 'message': 'Profile updated successfully.'})

        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        # Populate the form with existing user, profile, and company data
        initial_data = {
            'title': profile.title,
            'phone_no': profile.phone_no,
            'gender': profile.gender,
            'address': profile.address,
            'city': profile.city,
            'zipcode': profile.zipcode,
            'photo': profile.photo,
            'country': profile.country.id if profile.country else None,  # Check if country exists
            'state': profile.state.id if profile.state else None,
            'group': user.groups.first(),            
        }

        # Create the form with initial data
        form = UserProfileForm(initial=initial_data, instance=user)
    return render(request, 'my-profile.html', {
        'form': form,
        'user': user,
        'all_roles': all_roles,
        'countries': countries,
        'MEDIA_URL': settings.MEDIA_URL
    })

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password-reset-confirm.html'
    form_class = CustomPasswordResetConfirmForm
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def dispatch(self, *args, **kwargs):
        messages.success(self.request, "Password reset successfully. Please log in with your new password.")
        return redirect('login')
    

@staff_member_required
def clear_cache_view(request):
    cache.clear()
    messages.success(request, "Cache has been cleared successfully.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
