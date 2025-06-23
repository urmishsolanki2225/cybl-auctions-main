import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from adminpanel.models import Category
from adminpanel.forms import CategoryForm
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def all_category(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories').order_by('order')  # nulls last by default in PostgreSQL
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
    categories = Category.objects.filter(parent=None).order_by('order')
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
# def update_category(request):
#     if request.method == 'POST':
#         category_id = request.POST.get('categoryID')
#         new_name = request.POST.get('name', '').strip()
#         new_parent_id = request.POST.get('parentID')
#         new_image = request.POST.get('image', '').strip()
 
#         if not category_id or not new_name:
#             return JsonResponse({'status': 'error', 'message': 'Missing category ID or name.'})

#         if not category_id or not new_image:
#             return JsonResponse({'status': 'error', 'message': 'Missing image.'})
 
#         category = get_object_or_404(Category, id=category_id)
#         old_image = category.image   
 
#         if 'parentID' in request.POST:
#             if new_parent_id in [None, '', 'null']:
#                 category.parent = None
#             elif str(category.id) != new_parent_id:
#                 category.parent_id = new_parent_id  
#             else:
#                 return JsonResponse({'status': 'error', 'message': 'Category cannot be its own parent.'})
 
#         category.name = new_name

#         # Handle image upload - only if new image is provided
#         if 'image' in request.FILES and request.FILES['image']:
#             # Delete old image if exists
#             if old_image:
#                 if os.path.isfile(old_image.path):
#                     os.remove(old_image.path)
            
#             # Save new image with proper naming
#             ext = request.FILES['image'].name.split('.')[-1]
#             if category.parent:
#                 filename = f"{category.parent.name}_{category.id}.{ext}"
#             else:
#                 filename = f"{category.name}_{category.id}.{ext}"
            
#             category.image.save(filename, request.FILES['image'])
        
#         category.save()
 
#         data = {
#             'id': category.id,
#             'name': category.name,
#             'image': category.image.url if category.image else None,
#             'parent_id': category.parent.id if category.parent else None,
#             'parent_name': category.parent.name if category.parent else None,
#         }
 
#         message = 'Subcategory Updated successfully.' if category.parent else 'Category Updated successfully.'
#         return JsonResponse({'status': 'success', 'message': message, 'category': data})
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
    
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
