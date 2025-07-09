from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from adminpanel.models import Category, Auctions, Inventory, Media, Bid, CategoryMetaField, InventoryMetaValue
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from adminpanel.forms import InventoryForm 
import random
import string
import os, json
import uuid
from django.utils import timezone
from django.db.models import Q
from django.db.models import Count


@login_required(login_url='login')
def all_inventory(request, tabId):
    categories = Category.objects.filter(parent__isnull=False)

    pending_inventory = Inventory.objects.filter(status='pending')\
        .prefetch_related('media_items')\
        .order_by('-created_at')

    in_auction_inventory = Inventory.objects.filter(status='auction')\
        .select_related('auction')\
        .prefetch_related('media_items')\
        .order_by('-created_at')

    sold_inventory = Inventory.objects.filter(status='sold')\
        .select_related('auction')\
        .prefetch_related('media_items')\
        .order_by('-created_at')

    unsold_inventory = Inventory.objects.filter(winning_bid__isnull=True, status='unsold')\
        .prefetch_related('media_items')\
        .order_by('-created_at')

    in_transit_inventory = Inventory.objects.filter(in_transit_status__isnull=False)\
        .prefetch_related('media_items')\
        .order_by('-created_at')

    upcoming_auctions = Auctions.objects.filter(
        status='next'
    ).order_by('created_at')

    return render(request, 'inventory/index.html', {
        'current_tab': tabId,
        'pending_inventory': pending_inventory,
        'in_auction_inventory': in_auction_inventory,
        'sold_inventory': sold_inventory,
        'unsold_inventory': unsold_inventory,
        'in_transit_inventory': in_transit_inventory,
        'categories': categories,
        'auctions': upcoming_auctions,
        'MEDIA_URL': settings.MEDIA_URL
    })


  
def generate_inventory_number():
    while True:
        inventory_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if not Inventory.objects.filter(inventory_number=inventory_number).exists():
            return inventory_number
        
# Add this method to your view class or as a separate function
# Add this method to your view class or as a separate function
def validate_meta_fields(request, category_id):
    """
    Validate meta fields for a given category
    Returns a dictionary of errors if any, empty dict if all valid
    """
    errors = {}
    
    if not category_id:
        return errors
    
    try:
        category = Category.objects.get(id=category_id)
        
        # Debug: Check all meta fields first
        all_meta_fields = CategoryMetaField.objects.filter(category=category)
        print(f"Debug - All meta fields for category {category_id}:")
        for field in all_meta_fields:
            print(f"  Field ID: {field.id}, Name: {field.name}, Type: {field.field_type}, Required: {field.is_required}")
        
        # Now check only required fields
        meta_fields = CategoryMetaField.objects.filter(category=category, is_required=True)
        print(f"Debug - Required meta fields count: {meta_fields.count()}")
        
        for meta_field in meta_fields:
            field_name = f'meta_{meta_field.id}'
            
            if meta_field.field_type == 'checkbox':
                # For checkboxes, check if any values are selected
                field_values = request.POST.getlist(field_name)
                print(f"Debug - Checkbox {field_name}: {field_values}")
                # Treat empty list or list of empty strings as invalid
                if not field_values or all(v.strip() == '' for v in field_values):
                    errors[field_name] = [f'{meta_field.name} is required.']
                    
            elif meta_field.field_type == 'toggle':
                # For toggle, check if it's checked (value will be 'Yes' if checked)
                field_value = request.POST.get(field_name)
                print(f"Debug - Toggle {field_name}: {field_value}")
                if not field_value:
                    errors[field_name] = [f'{meta_field.name} is required.']
                    
            elif meta_field.field_type == 'radio':
                # For radio buttons
                field_value = request.POST.get(field_name)
                print(f"Debug - Radio {field_name}: {field_value}")
                if not field_value:
                    errors[field_name] = [f'{meta_field.name} is required.']
                    
            else:
                # For input, textarea, select field types
                field_value = request.POST.get(field_name)
                print(f"Debug - Other {field_name}: {field_value}")
                if not field_value or field_value.strip() == '':
                    errors[field_name] = [f'{meta_field.name} is required.']
    
    except Category.DoesNotExist:
        print(f"Debug - Category {category_id} does not exist")
        pass
    
    return errors

# Update your create_inventory view
@login_required(login_url='login')
def create_inventory(request):
    categories = Category.objects.filter(is_active=True).order_by('id')
    current_date = timezone.now()
    upcoming_auctions = Auctions.objects.filter(start_date__gt=current_date).order_by('start_date')

    starting_bid_amounts = (
        [i for i in range(50, 1001, 50)] +
        [i for i in range(1100, 2001, 100)]
    )
    
    # Get active categories with their meta fields
    active_categories = Category.objects.filter(is_active=True).prefetch_related('meta_fields')
   
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        
        # Validate meta fields
        category_id = request.POST.get('category')
        meta_errors = validate_meta_fields(request, category_id)
        
        if form.is_valid() and not meta_errors:
            inventory_item = form.save(commit=False)
            inventory_item.inventory_number = generate_inventory_number()

            if inventory_item.reserve_price is None:
                inventory_item.reserve_price = 0

            inventory_item.save()
            
            # Handle meta field values (existing code)
            if category_id:
                category = Category.objects.get(id=category_id)
                meta_fields = CategoryMetaField.objects.filter(category=category)
                
                for meta_field in meta_fields:
                    field_name = f'meta_{meta_field.id}'
                    
                    if meta_field.field_type == 'checkbox':
                        field_values = request.POST.getlist(field_name)
                        if field_values:
                            field_value = ','.join(field_values)
                            InventoryMetaValue.objects.create(
                                inventory=inventory_item,
                                meta_field=meta_field,
                                value=field_value
                            )
                    else:
                        field_value = request.POST.get(field_name)
                        if field_value:
                            InventoryMetaValue.objects.create(
                                inventory=inventory_item,
                                meta_field=meta_field,
                                value=field_value
                            )
                            
            # Handle media file uploads (existing code)
            files = request.FILES.getlist('images[]')
            for uploaded_file in files:
                folder_path = os.path.join(settings.MEDIA_ROOT, 'inventory', str(inventory_item.id))
                os.makedirs(folder_path, exist_ok=True)

                unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
                file_path = os.path.join(folder_path, unique_filename)

                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                Media.objects.create(
                    inventory=inventory_item,
                    name=unique_filename,
                    path=os.path.join('inventory', str(inventory_item.id), unique_filename),
                    size=uploaded_file.size,
                    entity='inventory',
                    type='IMAGE'
                )

            return JsonResponse({
                'success': True,
                'inventory_id': inventory_item.id
            })

        # Merge form errors with meta field errors
        all_errors = dict(form.errors)
        all_errors.update(meta_errors)
        
        return JsonResponse({'success': False, 'errors': all_errors})

    return render(request, 'inventory/create.html', {
        'auctions': upcoming_auctions,
        'starting_bid_amounts': starting_bid_amounts,
        'categories': categories,
        'active_categories': active_categories,
    })

# Update your edit_inventory view
@login_required(login_url='login')
def edit_inventory(request, inventory_id):
    inventory_item = get_object_or_404(Inventory, id=inventory_id)
    images = Media.objects.filter(inventory=inventory_item).order_by('order')
    categories = Category.objects.filter(is_active=True).order_by('id')
    current_date = timezone.now()
    
    # Get active categories with their meta fields
    active_categories = Category.objects.filter(is_active=True).prefetch_related('meta_fields')
    
    # Get existing meta values for this inventory
    existing_meta_values = {}
    if inventory_item.category:
        meta_values = InventoryMetaValue.objects.filter(inventory=inventory_item)
        for meta_value in meta_values:
            if meta_value.meta_field.field_type == 'checkbox':
                existing_meta_values[meta_value.meta_field.id] = {
                    'value': meta_value.value.split(','),
                    'field_type': meta_value.meta_field.field_type
                }
            else:
                existing_meta_values[meta_value.meta_field.id] = {
                    'value': meta_value.value,
                    'field_type': meta_value.meta_field.field_type
                }

    # Include both running and upcoming auctions
    auctions = Auctions.objects.filter(
        Q(start_date__gt=current_date) |
        Q(start_date__lte=current_date)
    ).order_by('start_date')

    starting_bid_amounts = (
        [i for i in range(50, 1001, 50)] +
        [i for i in range(1100, 2001, 100)]
    )

    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory_item)
        
        # Validate meta fields
        category_id = request.POST.get('category')
        meta_errors = validate_meta_fields(request, category_id)
        
        if form.is_valid() and not meta_errors:
            if form.cleaned_data.get('reserve_price') is None:
                inventory_item.reserve_price = 0
            else:
                inventory_item.reserve_price = form.cleaned_data.get('reserve_price')

            form.save()
            
            # Handle meta field values update (existing code)
            if category_id:
                InventoryMetaValue.objects.filter(inventory=inventory_item).delete()
                
                category = Category.objects.get(id=category_id)
                meta_fields = CategoryMetaField.objects.filter(category=category)
                
                for meta_field in meta_fields:
                    field_name = f'meta_{meta_field.id}'
                    
                    if meta_field.field_type == 'checkbox':
                        field_values = request.POST.getlist(field_name)
                        if field_values:
                            field_value = ','.join(field_values)
                            InventoryMetaValue.objects.create(
                                inventory=inventory_item,
                                meta_field=meta_field,
                                value=field_value
                            )
                    else:
                        field_value = request.POST.get(field_name)
                        if field_value:
                            InventoryMetaValue.objects.create(
                                inventory=inventory_item,
                                meta_field=meta_field,
                                value=field_value
                            )
                        
            return JsonResponse({'success': True})

        # Merge form errors with meta field errors
        all_errors = dict(form.errors)
        all_errors.update(meta_errors)
        
        return JsonResponse({'success': False, 'errors': all_errors})

    # Pre-fill the form with the existing instance data
    inventory_form = InventoryForm(instance=inventory_item)

    return render(request, 'inventory/edit.html', {
        'auctions': auctions,
        'starting_bid_amounts': starting_bid_amounts,
        'categories': categories,
        'active_categories': active_categories,
        'form': inventory_form,
        'inventory_item': inventory_item,
        'images': images,
        'MEDIA_URL': settings.MEDIA_URL,
        'existing_meta_values': existing_meta_values,
    })

@login_required(login_url='login')
def upload_images(request, inventory_id):
    if request.method == 'POST':
        inventory = get_object_or_404(Inventory, id=inventory_id)
        files = request.FILES.getlist('files')

        for file in files:
            # Generate a unique file name using uuid
            unique_filename = str(uuid.uuid4()) + os.path.splitext(file.name)[1]
            # Define the path where the file will be saved
            item_folder = os.path.join(settings.MEDIA_ROOT, 'inventory', str(inventory_id))
            if not os.path.exists(item_folder):
                os.makedirs(item_folder)  # Create the inventory_id folder if it doesn't exist

            # Constructing the relative path for the media
            relative_path = os.path.join('inventory', str(inventory_id), unique_filename)

            # Calculate the size of the file
            size = file.size  # This gives the size in bytes

            # Saving the media object with the constructed path
            media = Media(
                inventory=inventory,
                name=unique_filename,
                path=relative_path,
                size=size,
                entity='inventory',
                type='IMAGE'
            )
            with open(os.path.join(settings.MEDIA_ROOT, relative_path), 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            media.save()

        return JsonResponse({'success': True, 'message': 'Images uploaded successfully!', 'inventory_id': inventory.id})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required(login_url='login')
@csrf_exempt
def update_image_order(request, inventory_id):
    if request.method == 'POST':
        try:
            # Load JSON data
            data = json.loads(request.body)
            order = data.get('order', [])
            inventory = get_object_or_404(Inventory, id=inventory_id)

            # Create a mapping of file names to Media IDs
            media_map = {media.name: media.id for media in Media.objects.filter(inventory=inventory)}

            # Update the order based on file names
            for index, file_name in enumerate(order):
                if file_name in media_map:
                    Media.objects.filter(id=media_map[file_name], inventory=inventory).update(order=index)

            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required(login_url='login')
def delete_image(request, inventory_id):
    if request.method == 'POST':
        item = get_object_or_404(Inventory, id=inventory_id)
        filename = request.POST.get('filename')
        media = get_object_or_404(Media, inventory=item, name=filename, type='IMAGE')

        file_path = os.path.join(settings.MEDIA_ROOT, media.path)
        if os.path.exists(file_path):
            os.remove(file_path)

        media.delete()
        return JsonResponse({'success': True, 'message': 'Image deleted successfully!'})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required(login_url='login')
def delete_inventory(request):
    inventory_id = request.POST.get('itemId')
    inventory = get_object_or_404(Inventory, id=inventory_id)

    try:
        inventory.delete()
        return JsonResponse({'status': 'success', 'message': 'Inventory has been deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'There was an error deleting the item.'})

#Bid History
@login_required(login_url='login')
def bidding_history(request, inventory_id):
    # Get the bids for the specific inventory along with user profile and related country/state
    bids = Bid.objects.filter(inventory_id=inventory_id).select_related(
        'user',                # Directly access the user
        'user__profile',       # Then access the profile
        'user__profile__country',  # Country related to Profile
        'user__profile__state'  # State related to Profile
    ).values(
        'user__username',
        'user__first_name',         # Accessing first name from User model
        'user__last_name',          # Accessing last name from User model
        'user__profile__phone_no',
        'user__profile__address',
        'user__profile__zipcode',
        'user__profile__city',
        'user__profile__country__name',  # Country name
        'user__profile__country__alpha2Code',  # Country alpha2Code
        'user__profile__state__name',  # State name
        'bid_amount',
        'type',
        'created_at'
    )

    # Prepare the bidding data for JSON response
    bidding_data = [{
        'user': f"{bid['user__first_name']} {bid['user__last_name']}",
        'phone_no': bid['user__profile__phone_no'],
        'address': bid['user__profile__address'],
        'city': bid['user__profile__city'],
        'zipcode': bid['user__profile__zipcode'],
        'country': bid['user__profile__country__name'],
        'country_code': bid['user__profile__country__alpha2Code'],
        'state': bid['user__profile__state__name'],
        'amount': bid['bid_amount'],
        'type': bid['type'],
        'timestamp': bid['created_at']
    } for bid in bids]

    return JsonResponse({'bids': bidding_data})
