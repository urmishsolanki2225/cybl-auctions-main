from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from adminpanel.models import CategoryMetaField, Category
from adminpanel.forms import CategoryMetaFieldForm
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def meta_fields_view(request):
    active_category = Category.objects.filter(is_active=True).first()
    meta_fields = CategoryMetaField.objects.filter(category=active_category)
    return render(request, 'category/meta/category-meta.html', {
        'active_category': active_category,
        'meta_fields': meta_fields
    })

@require_http_methods(["GET"])
def fetch_meta_fields(request):
    meta_fields = CategoryMetaField.objects.select_related('category').order_by('-id')
    data = [{
        'id': mf.id,
        'category_name': mf.category.name,
        'name': mf.name,
        'field_type': mf.field_type,
        'field_type_display': mf.get_field_type_display(),
        'field_options': mf.field_options,
        'options_list': mf.get_options_list(),
        'is_filter': mf.is_filter,
        'is_required': mf.is_required
    } for mf in meta_fields]
    return JsonResponse({'status': 'success', 'meta_fields': data})

@csrf_exempt
@require_http_methods(["POST"])
def save_meta_field(request):
    try:
        meta_field_id = request.POST.get('meta_field_id')
        active_category = Category.objects.filter(is_active=True).first()
        
        if not active_category:
            return JsonResponse({
                'status': 'error',
                'message': 'No active category found'
            }, status=400)
        
        # Get or create meta field instance
        if meta_field_id:
            meta_field = CategoryMetaField.objects.get(id=meta_field_id)
        else:
            meta_field = CategoryMetaField(category=active_category)
        
        # Create form instance
        form = CategoryMetaFieldForm(request.POST, instance=meta_field)
        
        if form.is_valid():
            form.save()
            message = 'Meta field updated successfully' if meta_field_id else 'Meta field created successfully'
            return JsonResponse({
                'status': 'success',
                'message': message,
                'id': meta_field.id
            })
        else:
            # Return form errors
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = field_errors
            
            return JsonResponse({
                'status': 'error',
                'message': 'Please correct the errors below',
                'errors': errors
            }, status=400)
        
    except CategoryMetaField.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Meta field not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def delete_meta_field(request):
    try:
        meta_field_id = request.POST.get('meta_field_id')
        meta_field = CategoryMetaField.objects.get(id=meta_field_id)
        meta_field.delete()
        return JsonResponse({'status': 'success', 'message': 'Meta field deleted successfully'})
    except CategoryMetaField.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Meta field not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)