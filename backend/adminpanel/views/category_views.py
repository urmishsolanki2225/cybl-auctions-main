import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from adminpanel.models import Category,CategoryCharge, ChargeType, CategoryMetaField
from adminpanel.forms import CategoryForm
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect  
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='login')
def all_category(request):
    categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories').order_by('order')  # nulls last by default in PostgreSQL
    return render(request, 'category/index.html', {'categories': categories, 'active_tab': 'allcategory'})

@login_required(login_url='login')
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)  # Include request.FILES here
        if form.is_valid():
            # First validate the image before saving anything
            if 'image' in request.FILES:
                ext = request.FILES['image'].name.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Invalid image format. Only JPG, JPEG, PNG, and WEBP are allowed.',
                    })
            
            # Only save if everything is valid
            category = form.save(commit=False)  # Don't save to DB yet
            
            # Handle image upload
            if 'image' in request.FILES:
                ext = request.FILES['image'].name.split('.')[-1].lower()
                if category.parent:
                    filename = f"{category.parent.name}_{category.id}.{ext}"
                else:
                    filename = f"{category.name}_{category.id}.{ext}"
                
                category.image.save(filename, request.FILES['image'])
            
            # Now save to database
            category.save()
            
            data = {
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent.id if category.parent else None,
                'parent_name': category.parent.name if category.parent else None,
                'image': category.image.url if category.image else None,
            }
            
            message = 'Subcategory created successfully.' if category.parent else 'Category created successfully.'
            return JsonResponse({'status': 'success', 'message': message, 'category': data})
        else:
            # Convert form errors to proper format
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            
            return JsonResponse({
                'status': 'error',
                'message': 'Please correct the errors below.',
                'errors': errors
            })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        })

@login_required(login_url='login')
def get_category(request):
    category_id = request.GET.get('category_id')
    category = get_object_or_404(Category, id=category_id)
    data = {
        'id': category.id,
        'name': category.name,
        'parent_id': category.parent.id if category.parent else None,       
        'image': category.image.url if category.image else None,     
    }
    return JsonResponse({'status': 'success', 'category': data})

@login_required(login_url='login')
def fetch_categories(request):
    categories = Category.objects.filter(parent=None, is_active=True).order_by('order')
    categories_data = []

    for category in categories:
        subcategories = category.subcategories.all()
        subcategories_data = [{
            'id': subcat.id, 
            'name': subcat.name,
            } for subcat in subcategories]

        categories_data.append({
            'id': category.id,
            'name': category.name,
            'subcategories': subcategories_data
        })

    return JsonResponse({'status': 'success', 'categories': categories_data})
    
@login_required(login_url='login')
def update_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        category_id = request.POST.get('categoryID')
        new_name = request.POST.get('name', '').strip()
        new_parent_id = request.POST.get('parentID')

        if not category_id or not new_name:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing category ID or name.',
                'errors': {
                    'name': ['Category name is required.'] if not new_name else [],
                    'categoryID': ['Category ID is required.'] if not category_id else []
                }
            })

        category = get_object_or_404(Category, id=category_id)
        old_image = category.image

        # Only check for duplicate name if the name is actually being changed
        if new_name != category.name:
            # Use the form's clean method to validate name uniqueness
            form.instance = category
            if not form.is_valid():
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please correct the errors below.',
                    'errors': errors
                })

        # Validate image before making any changes
        if 'image' in request.FILES:
            ext = request.FILES['image'].name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid image format. Only JPG, JPEG, PNG, and WEBP are allowed.',
                    'errors': {
                        'image': ['Invalid image format. Only JPG, JPEG, PNG, and WEBP are allowed.']
                    }
                })

        # Only proceed with updates if validations pass
        try:
            # Handle parent change
            if 'parentID' in request.POST:
                if new_parent_id in [None, '', 'null']:
                    category.parent = None
                elif str(category.id) != new_parent_id:
                    category.parent_id = new_parent_id
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Category cannot be its own parent.',
                        'errors': {
                            'parentID': ['Category cannot be its own parent.']
                        }
                    })

            # Only update name if it's changed
            if new_name != category.name:
                category.name = new_name

            # Handle image upload if validation passed
            if 'image' in request.FILES:
                # Delete old image if exists
                if old_image and os.path.isfile(old_image.path):
                    os.remove(old_image.path)
                
                # Save new image with proper naming
                ext = request.FILES['image'].name.split('.')[-1].lower()
                if category.parent:
                    filename = f"{category.parent.name}_{category.id}.{ext}"
                else:
                    filename = f"{category.name}_{category.id}.{ext}"
                
                category.image.save(filename, request.FILES['image'])

            category.save()

            data = {
                'id': category.id,
                'name': category.name,
                'image': category.image.url if category.image else None,
                'parent_id': category.parent.id if category.parent else None,
                'parent_name': category.parent.name if category.parent else None,
            }

            message = 'Subcategory updated successfully.' if category.parent else 'Category updated successfully.'
            return JsonResponse({'status': 'success', 'message': message, 'category': data})

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to update category.',
                'errors': {
                    '__all__': [str(e)]
                }
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.',
        'errors': {
            '__all__': ['Only POST requests are allowed.']
        }
    })
    
@login_required(login_url='login')
def update_category_order(request):
    if request.method == 'POST':
        order = request.POST.getlist('order[]')
        for index, category_id in enumerate(order):
            Category.objects.filter(id=category_id).update(order=index)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required(login_url='login')
def delete_category(request):
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            # Delete associated image file
            if category.image:
                if os.path.isfile(category.image.path):
                    os.remove(category.image.path)
            category.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': 'Failed to delete category.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method or not AJAX request.'})

#####################################################################################################
#charges type add
from django.db import IntegrityError
def manage_charge_types(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        
        errors = {}
        
        # Validation
        if not name:
            errors['name'] = 'Name is required'
        if not code:
            errors['code'] = 'Code is required'
        elif ChargeType.objects.filter(code=code).exists():
            errors['code'] = 'This code already exists'
            
        if errors:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': errors}, status=400)
            else:
                for field, message in errors.items():
                    messages.error(request, f"{field}: {message}")
                return redirect('manage_charge_types')
        
        try:
            charge_type = ChargeType.objects.create(
                name=name,
                code=code,
                description=description
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'charge_type': {
                        'id': charge_type.id,
                        'name': charge_type.name,
                        'code': charge_type.code,
                        'description': charge_type.description
                    }
                })
            else:
                messages.success(request, 'Charge type added successfully')
                return redirect('manage_charge_types')
                
        except IntegrityError as e:
            if 'name' in str(e):
                error = {'name': 'This name already exists'}
            elif 'code' in str(e):
                error = {'code': 'This code already exists'}
            else:
                error = {'error': str(e)}
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': error}, status=400)
            else:
                messages.error(request, list(error.values())[0])
                return redirect('manage_charge_types')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=500)
            else:
                messages.error(request, f'Error: {str(e)}')
                return redirect('manage_charge_types')
    
    # GET request handling
    charge_types = ChargeType.objects.all().order_by('-id')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'charge_types': list(charge_types.values())
        })
    else:
        return render(request, 'category/manage_charge_types.html', {
            'charge_types': charge_types
        })

def toggle_charge_type(request, pk):
    try:
        charge_type = ChargeType.objects.get(pk=pk)
        charge_type.is_active = not charge_type.is_active
        charge_type.save()
        return JsonResponse({'success': True, 'is_active': charge_type.is_active})
    except ChargeType.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Charge type not found'})

@require_POST
def delete_charge_type(request, pk):
    try:
        charge_type = ChargeType.objects.get(pk=pk)
        
        # Check if this charge type is being used
        # You might want to add this check based on your CategoryCharge model
        if hasattr(charge_type, 'categorycharge_set') and charge_type.categorycharge_set.exists():
            return JsonResponse({
                'success': False, 
                'message': 'Cannot delete charge type as it is being used by categories'
            })
        
        charge_type.delete()
        return JsonResponse({
            'success': True, 
            'message': 'Charge type deleted successfully'
        })
        
    except ChargeType.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Charge type not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error deleting charge type: {str(e)}'
        })

@require_POST
def update_charge_type_name(request, pk):
    try:
        charge_type = ChargeType.objects.get(pk=pk)
        new_name = request.POST.get('name', '').strip()
        
        if not new_name:
            return JsonResponse({
                'success': False,
                'message': 'Name cannot be empty'
            })
        
        # Check if name already exists (excluding current charge type)
        if ChargeType.objects.filter(name=new_name).exclude(pk=pk).exists():
            return JsonResponse({
                'success': False,
                'message': 'This name already exists'
            })
        
        charge_type.name = new_name
        charge_type.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Name updated successfully',
            'new_name': new_name
        })
        
    except ChargeType.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Charge type not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating name: {str(e)}'
        })

#charges add
def category_charges_view(request):
    # Get all active parent categories only
    categories = Category.objects.filter(deleted_at__isnull=True, parent__isnull=True, is_active=True)
    
    # Get all active charge types
    charge_types = ChargeType.objects.filter(is_active=True).order_by('name')
    
    # Prepare data structure
    categories_data = []
    
    # Prefetch all charges for these categories
    existing_charges = CategoryCharge.objects.filter(
        category__in=categories,
        charge_type__in=charge_types
    ).select_related('charge_type')
    
    # Create a dictionary of charges for each category
    charges_dict = {}
    for charge in existing_charges:
        if charge.category.id not in charges_dict:
            charges_dict[charge.category.id] = {}
        charges_dict[charge.category.id][charge.charge_type.code] = charge.amount
    
    # Build the final data structure
    for category in categories:
        category_charges = charges_dict.get(category.id, {})
        
        # Create a list of charge values in the same order as charge_types
        charge_values = []
        for charge_type in charge_types:
            charge_values.append({
                'code': charge_type.code,
                'value': category_charges.get(charge_type.code, 0)
            })
        
        categories_data.append({
            'category': category,
            'charge_values': charge_values  # Now we have ordered list of values
        })
    
    context = {
        'categories_data': categories_data,
        'charge_types': charge_types
    }
    
    return render(request, 'category/cat-charges.html', context)

@require_POST
def save_category_charges(request):
    try:
        data = json.loads(request.POST.get('charges', '[]'))
        
        for charge_data in data:
            category_id = charge_data.get('category_id')
            charge_type_code = charge_data.get('charge_type')
            amount = charge_data.get('amount', 0)
            
            try:
                charge_type = ChargeType.objects.get(code=charge_type_code)
                category = Category.objects.get(id=category_id)
                
                # Get or create the charge
                charge, created = CategoryCharge.objects.get_or_create(
                    category=category,
                    charge_type=charge_type,
                    defaults={'amount': amount}
                )
                
                # Update if not created
                if not created:
                    charge.amount = amount
                    charge.save()
            
            except (ChargeType.DoesNotExist, Category.DoesNotExist) as e:
                continue
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
def save_single_charge(request):
    try:
        category_id = request.POST.get('category_id')
        charge_type_code = request.POST.get('charge_type')
        amount = request.POST.get('amount', 0)
        
        charge_type = ChargeType.objects.get(code=charge_type_code)
        category = Category.objects.get(id=category_id)
        
        # Get or create the charge
        charge, created = CategoryCharge.objects.get_or_create(
            category=category,
            charge_type=charge_type,
            defaults={'amount': amount}
        )
        
        # Update if not created
        if not created:
            charge.amount = amount
            charge.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
        