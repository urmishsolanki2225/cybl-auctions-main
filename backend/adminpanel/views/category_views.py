from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from adminpanel.models import Category
from adminpanel.forms import CategoryForm
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def all_category(request):
    categories = Category.objects.all()   
    return render(request, 'category/index.html', {'categories': categories, 'active_tab': 'allcategory'})

@login_required(login_url='login')
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()           
            data = {
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent.id if category.parent else None,
                'parent_name': category.parent.name if category.parent else None,
            }
            
            if category.parent:
                message = 'Subcategory created successfully.'
            else:
                message = 'Category created successfully.'
            
            return JsonResponse({'status': 'success', 'message': message, 'category': data})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'Invalid form submission.', 'errors': errors})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required(login_url='login')
def get_category(request):
    category_id = request.GET.get('category_id')
    category = get_object_or_404(Category, id=category_id)
    data = {
        'id': category.id,
        'name': category.name,
        'parent_id': category.parent.id if category.parent else None,       
    }
    return JsonResponse({'status': 'success', 'category': data})

@login_required(login_url='login')
def fetch_categories(request):
    categories = Category.objects.filter(parent=None).order_by('order')
    categories_data = []

    for category in categories:
        subcategories = category.subcategories.all()
        subcategories_data = [{'id': subcat.id, 'name': subcat.name} for subcat in subcategories]

        categories_data.append({
            'id': category.id,
            'name': category.name,
            'subcategories': subcategories_data
        })

    return JsonResponse({'status': 'success', 'categories': categories_data})

@login_required(login_url='login')
def update_category(request):
    if request.method == 'POST':
        category_id = request.POST.get('categoryID')
        new_name = request.POST.get('name', '').strip()
        new_parent_id = request.POST.get('parentID')
 
        if not category_id or not new_name:
            return JsonResponse({'status': 'error', 'message': 'Missing category ID or name.'})
 
        category = get_object_or_404(Category, id=category_id)
 
        category.name = new_name
 
        if 'parentID' in request.POST:
            if new_parent_id in [None, '', 'null']:
                category.parent = None
            elif str(category.id) != new_parent_id:
                category.parent_id = new_parent_id  
            else:
                return JsonResponse({'status': 'error', 'message': 'Category cannot be its own parent.'})
 
        category.save()
 
        data = {
            'id': category.id,
            'name': category.name,
            'parent_id': category.parent.id if category.parent else None,
            'parent_name': category.parent.name if category.parent else None,
        }
 
        message = 'Subcategory Updated successfully.' if category.parent else 'Category Updated successfully.'
        return JsonResponse({'status': 'success', 'message': message, 'category': data})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
    
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
            category.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': 'Failed to delete category.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method or not AJAX request.'})
