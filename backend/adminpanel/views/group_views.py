from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from adminpanel.forms import GroupForm, PermissionForm
import random,string, json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# new permissions
@login_required(login_url='login')
def permissions_management(request):
    groups = Group.objects.all()
    permissions = Permission.objects.all()
    return render(request, 'groups/permissions.html', {'groups': groups, 'permissions': permissions, 'active_tab': 'groups'})

@csrf_exempt
@login_required(login_url='login')
def update_permissions(request):
    if request.method == 'POST':
        updates = json.loads(request.POST.get('updates'))
        for update in updates:
            group = Group.objects.get(id=update['group_id'])
            if group.name != 'Super Admin':
                permission = Permission.objects.get(id=update['permission_id'])
                if update['is_checked']:
                    group.permissions.add(permission)
                else:
                    group.permissions.remove(permission)

        # Ensure Super Admin has all permissions
        super_admin_group = Group.objects.get(name='Super Admin')
        all_permissions = Permission.objects.all()
        super_admin_group.permissions.set(all_permissions)

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required(login_url='login')
def groups_index(request):
    groups = Group.objects.all()
    return render(request, 'groups/index.html', {'all_groups': groups, 'active_tab': 'groups'})

@login_required(login_url='login')
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save() 
            response_data = {
                'id': new_group.id,  
                'name': new_group.name,  
                'permissions_count': new_group.permissions.count() 
            }
            return JsonResponse(response_data) 
        else:
            errors = form.errors.as_json()
            return JsonResponse(errors, status=400)  
    else:
        form = GroupForm()
    return render(request, 'groups/create.html', {'form': form, 'active_tab': 'groups'})

@login_required(login_url='login')
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role updated successfully.')
            return JsonResponse({'status': 'success','new_name': group.name})  
        else:
            print(form.errors)
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)

    elif request.method == 'GET':
        form = GroupForm(instance=group)
        return JsonResponse({
            'status': 'success',
            'data': {
                'group_id': group.id,
                'group_name': group.name,
            }
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required(login_url='login')
def delete_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        group.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required(login_url='login')
def view_permissions(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    permissions = group.permissions.all()
    return render(request, 'groups/view_permissions.html', {'group': group, 'permissions': permissions, 'active_tab': 'groups'})

@login_required(login_url='login')
def delete_permission(request, group_id, permission_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        permission = get_object_or_404(Permission, id=permission_id)
        group.permissions.remove(permission)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
