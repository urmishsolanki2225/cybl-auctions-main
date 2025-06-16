from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.views import View
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
import uuid
from datetime import datetime

from adminpanel.models import Payment_History, Inventory


@login_required(login_url='login')
def payment_history_index(request, tabId=None):
    status_mapping = {
        1: 'Pending',
        2: 'Completed',
        3: 'Refunded',
        4: 'Failed'
    }
    status = status_mapping.get(tabId)
    if status:
        payment_history = Payment_History.objects.filter(status=status)
    else:
        payment_history = Payment_History.objects.all()

    return render(request, 'payments/index.html', {
        'payment_history': payment_history,
        'tabId': status,
        'MEDIA_URL': settings.MEDIA_URL
    })


@login_required(login_url='login')
def InvoiceView(request, payment_id):
    payment = Payment_History.objects.get(id=payment_id)
    return render(request, 'payments/invoice.html', {
        'payment': payment,
        'MEDIA_URL': settings.MEDIA_URL
    })


@login_required(login_url='login')
def create_payment_history(request):
    """Create new payment history record"""
    if request.method == 'GET':
        # Get all users and inventories for dropdowns
        users = User.objects.filter(is_active=True).order_by('username')
        inventories = Inventory.objects.all().order_by('title')
        
        return render(request, 'payments/create.html', {
            'users': users,
            'inventories': inventories,
            'MEDIA_URL': settings.MEDIA_URL
        })
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                # Extract form data
                transaction_id = request.POST.get('transaction_id', '').strip()
                amount = request.POST.get('amount', '').strip()
                user_id = request.POST.get('user', '').strip()
                inventory_id = request.POST.get('inventory', '').strip()
                status = request.POST.get('status', '').strip()
                payment_method = request.POST.get('payment_method', '').strip()
                notes = request.POST.get('notes', '').strip()
                
                # Validation
                errors = {}
                
                # Validate amount
                if not amount:
                    errors['amount'] = ['Amount is required']
                else:
                    try:
                        amount_decimal = Decimal(amount)
                        if amount_decimal <= 0:
                            errors['amount'] = ['Amount must be greater than 0']
                    except (ValueError, TypeError):
                        errors['amount'] = ['Please enter a valid amount']
                
                # Validate user
                if not user_id:
                    errors['user'] = ['User is required']
                else:
                    try:
                        user = User.objects.get(id=user_id, is_active=True)
                    except User.DoesNotExist:
                        errors['user'] = ['Invalid user selected']
                
                # Validate inventory
                if not inventory_id:
                    errors['inventory'] = ['Inventory is required']
                else:
                    try:
                        inventory = Inventory.objects.get(id=inventory_id)
                    except Inventory.DoesNotExist:
                        errors['inventory'] = ['Invalid inventory selected']
                
                # Validate status
                if not status:
                    errors['status'] = ['Status is required']
                elif status not in [choice[0] for choice in Payment_History.PaymentStatus.choices]:
                    errors['status'] = ['Invalid status selected']
                
                # Validate payment method
                if not payment_method:
                    errors['payment_method'] = ['Payment method is required']
                elif payment_method not in [choice[0] for choice in Payment_History.PaymentMethod.choices]:
                    errors['payment_method'] = ['Invalid payment method selected']
                
                # Check if transaction_id is unique (if provided)
                if transaction_id:
                    if Payment_History.objects.filter(transaction_id=transaction_id).exists():
                        errors['transaction_id'] = ['Transaction ID already exists']
                
                # If there are validation errors, return them
                if errors:
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    })
                
                # Generate transaction ID if not provided
                if not transaction_id:
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    unique_id = str(uuid.uuid4())[:8].upper()
                    transaction_id = f"TXN{timestamp}{unique_id}"
                
                # Create the payment history record
                payment_history = Payment_History.objects.create(
                    transaction_id=transaction_id,
                    amount=amount_decimal,
                    user=user,
                    inventory=inventory,
                    status=status,
                    payment_method=payment_method
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Payment history record created successfully! Transaction ID: {transaction_id}',
                    'payment_id': payment_history.id
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'errors': {'general': [f'An error occurred: {str(e)}']}
            })


@login_required(login_url='login')
def edit_payment_history(request, payment_id):
    """Edit existing payment history record"""
    payment = get_object_or_404(Payment_History, id=payment_id)
    
    if request.method == 'GET':
        # Get all users and inventories for dropdowns
        users = User.objects.filter(is_active=True).order_by('username')
        inventories = Inventory.objects.all().order_by('title')
        
        return render(request, 'payments/edit.html', {
            'payment': payment,
            'users': users,
            'inventories': inventories,
            'MEDIA_URL': settings.MEDIA_URL
        })
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                # Extract form data
                transaction_id = request.POST.get('transaction_id', '').strip()
                amount = request.POST.get('amount', '').strip()
                user_id = request.POST.get('user', '').strip()
                inventory_id = request.POST.get('inventory', '').strip()
                status = request.POST.get('status', '').strip()
                payment_method = request.POST.get('payment_method', '').strip()
                
                # Validation
                errors = {}
                
                # Validate amount
                if not amount:
                    errors['amount'] = ['Amount is required']
                else:
                    try:
                        amount_decimal = Decimal(amount)
                        if amount_decimal <= 0:
                            errors['amount'] = ['Amount must be greater than 0']
                    except (ValueError, TypeError):
                        errors['amount'] = ['Please enter a valid amount']
                
                # Validate user
                if not user_id:
                    errors['user'] = ['User is required']
                else:
                    try:
                        user = User.objects.get(id=user_id, is_active=True)
                    except User.DoesNotExist:
                        errors['user'] = ['Invalid user selected']
                
                # Validate inventory
                if not inventory_id:
                    errors['inventory'] = ['Inventory is required']
                else:
                    try:
                        inventory = Inventory.objects.get(id=inventory_id)
                    except Inventory.DoesNotExist:
                        errors['inventory'] = ['Invalid inventory selected']
                
                # Validate status
                if not status:
                    errors['status'] = ['Status is required']
                elif status not in [choice[0] for choice in Payment_History.PaymentStatus.choices]:
                    errors['status'] = ['Invalid status selected']
                
                # Validate payment method
                if not payment_method:
                    errors['payment_method'] = ['Payment method is required']
                elif payment_method not in [choice[0] for choice in Payment_History.PaymentMethod.choices]:
                    errors['payment_method'] = ['Invalid payment method selected']
                
                # Check if transaction_id is unique (if changed)
                if transaction_id and transaction_id != payment.transaction_id:
                    if Payment_History.objects.filter(transaction_id=transaction_id).exclude(id=payment.id).exists():
                        errors['transaction_id'] = ['Transaction ID already exists']
                
                # If there are validation errors, return them
                if errors:
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    })
                
                # Update the payment history record
                payment.transaction_id = transaction_id
                payment.amount = amount_decimal
                payment.user = user
                payment.inventory = inventory
                payment.status = status
                payment.payment_method = payment_method
                payment.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Payment history record updated successfully! Transaction ID: {payment.transaction_id}',
                    'payment_id': payment.id
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'errors': {'general': [f'An error occurred: {str(e)}']}
            })


@login_required(login_url='login')
def delete_payment_history(request):
    """Soft delete payment history record"""
    if request.method == 'POST':
        payment_id = request.POST.get('Trans_Id')
        try:
            payment = get_object_or_404(Payment_History, id=payment_id)
            payment.deleted_at = datetime.now()
            payment.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Payment history record deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'status': False,
                'message': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({
        'status': False,
        'message': 'Invalid request method'
    })

@login_required(login_url='login')
def get_inventory_details(request, inventory_id):
    """Get inventory details for AJAX calls"""
    try:
        inventory = Inventory.objects.get(id=inventory_id)
        return JsonResponse({
            'success': True,
            'data': {
                'id': inventory.id,
                'title': inventory.title,
                'price': float(inventory.price) if hasattr(inventory, 'price') else 0,
                # Add other inventory fields as needed
            }
        })
    except Inventory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Inventory not found'
        })


@login_required(login_url='login')
def get_user_details(request, user_id):
    """Get user details for AJAX calls"""
    try:
        user = User.objects.get(id=user_id, is_active=True)
        return JsonResponse({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip()
            }
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        })