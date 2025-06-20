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
from adminpanel.models import Payment_History, Inventory, PaymentChargeDetail


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
    
    # Calculate buyer's premium
    buyers_premium = 0
    if payment.inventory.auction and payment.inventory.auction.buyers_premium:
        buyers_premium = (payment.amount * payment.inventory.auction.buyers_premium) / 100
    
    # Get all payment charges
    payment_charges = payment.charge_details.all()
    total_charges = sum([charge.total_amount for charge in payment_charges])
    
    # Calculate grand total
    grand_total = payment.amount + buyers_premium + total_charges
    
    return render(request, 'payments/invoice.html', {
        'payment': payment,
        'buyers_premium': buyers_premium,
        'payment_charges': payment_charges,
        'total_charges': total_charges,
        'grand_total': grand_total,
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


# @login_required(login_url='login')
# def edit_payment_history(request, payment_id):
#     """Edit existing payment history record"""
#     payment = get_object_or_404(Payment_History, id=payment_id)
    
#     if request.method == 'GET':
#         # Get all users and inventories for dropdowns
#         users = User.objects.filter(is_active=True).order_by('username')
#         inventories = Inventory.objects.all().order_by('title')
        
#         return render(request, 'payments/edit.html', {
#             'payment': payment,
#             'users': users,
#             'inventories': inventories,
#             'MEDIA_URL': settings.MEDIA_URL
#         })
    
#     elif request.method == 'POST':
#         try:
#             with transaction.atomic():
#                 # Extract form data
#                 transaction_id = request.POST.get('transaction_id', '').strip()
#                 amount = request.POST.get('amount', '').strip()
#                 user_id = request.POST.get('user', '').strip()
#                 inventory_id = request.POST.get('inventory', '').strip()
#                 status = request.POST.get('status', '').strip()
#                 payment_method = request.POST.get('payment_method', '').strip()
                
#                 # Validation
#                 errors = {}
                
#                 # Validate amount
#                 if not amount:
#                     errors['amount'] = ['Amount is required']
#                 else:
#                     try:
#                         amount_decimal = Decimal(amount)
#                         if amount_decimal <= 0:
#                             errors['amount'] = ['Amount must be greater than 0']
#                     except (ValueError, TypeError):
#                         errors['amount'] = ['Please enter a valid amount']
                
#                 # Validate user
#                 if not user_id:
#                     errors['user'] = ['User is required']
#                 else:
#                     try:
#                         user = User.objects.get(id=user_id, is_active=True)
#                     except User.DoesNotExist:
#                         errors['user'] = ['Invalid user selected']
                
#                 # Validate inventory
#                 if not inventory_id:
#                     errors['inventory'] = ['Inventory is required']
#                 else:
#                     try:
#                         inventory = Inventory.objects.get(id=inventory_id)
#                     except Inventory.DoesNotExist:
#                         errors['inventory'] = ['Invalid inventory selected']
                
#                 # Validate status
#                 if not status:
#                     errors['status'] = ['Status is required']
#                 elif status not in [choice[0] for choice in Payment_History.PaymentStatus.choices]:
#                     errors['status'] = ['Invalid status selected']
                
#                 # Validate payment method
#                 if not payment_method:
#                     errors['payment_method'] = ['Payment method is required']
#                 elif payment_method not in [choice[0] for choice in Payment_History.PaymentMethod.choices]:
#                     errors['payment_method'] = ['Invalid payment method selected']
                
#                 # Check if transaction_id is unique (if changed)
#                 if transaction_id and transaction_id != payment.transaction_id:
#                     if Payment_History.objects.filter(transaction_id=transaction_id).exclude(id=payment.id).exists():
#                         errors['transaction_id'] = ['Transaction ID already exists']
                
#                 # If there are validation errors, return them
#                 if errors:
#                     return JsonResponse({
#                         'success': False,
#                         'errors': errors
#                     })
                
#                 # Update the payment history record
#                 payment.transaction_id = transaction_id
#                 payment.amount = amount_decimal
#                 payment.user = user
#                 payment.inventory = inventory
#                 payment.status = status
#                 payment.payment_method = payment_method
#                 payment.save()
                
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Payment history record updated successfully! Transaction ID: {payment.transaction_id}',
#                     'payment_id': payment.id
#                 })
                
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'errors': {'general': [f'An error occurred: {str(e)}']}
#             })
# views.py - Updated portions

@login_required(login_url='login')
def edit_payment_history(request, payment_id):
    """Edit existing payment history record"""
    payment = get_object_or_404(Payment_History, id=payment_id)
    
    if request.method == 'GET':
        # Get all users and inventories for dropdowns
        users = User.objects.filter(is_active=True).order_by('username')
        inventories = Inventory.objects.all().order_by('title')
        
        # Get existing charges for this payment
        existing_charges = payment.charge_details.filter(deleted_at__isnull=True)
        
        return render(request, 'payments/edit.html', {
            'payment': payment,
            'users': users,
            'inventories': inventories,
            'existing_charges': existing_charges,
            'charge_types': PaymentChargeDetail.ChargeType.choices,
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
                
                # Validation (keeping existing validation logic)
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
def add_payment_charge(request):
    """Add charge to payment"""
    if request.method == 'POST':
        print("Received POST request to add_payment_charge")  # Debug
        print("POST data:", request.POST)  # Debug
        try:
            with transaction.atomic():
                payment_id = request.POST.get('payment_id')
                charge_type = request.POST.get('charge_type')
                description = request.POST.get('description', '').strip()
                per_day_amount = request.POST.get('per_day_amount', '').strip()
                days = request.POST.get('days', '').strip()

                print(f"Raw data - payment_id: {payment_id}, charge_type: {charge_type}, amount: {per_day_amount}, days: {days}")  # Debug
                
                # Validation
                errors = {}
                
                # Validate payment
                try:
                    payment = Payment_History.objects.get(id=payment_id)
                    print(f"Found payment: {payment.id}")  # Debug
                except Payment_History.DoesNotExist:
                    errors['payment'] = ['Invalid payment selected']
                    print("Payment not found")  # Debug
                
                # Validate charge type
                if not charge_type:
                    errors['charge_type'] = ['Charge type is required']
                elif charge_type not in [choice[0] for choice in PaymentChargeDetail.ChargeType.choices]:
                    errors['charge_type'] = ['Invalid charge type selected']
                
                # Validate per_day_amount
                if not per_day_amount:
                    errors['per_day_amount'] = ['Per day amount is required']
                else:
                    try:
                        # Clean the amount string - remove any non-numeric characters except decimal point
                        cleaned_amount = ''.join(c for c in per_day_amount if c.isdigit() or c == '.')
                        if not cleaned_amount:
                            raise ValueError("No numeric characters found")
                        
                        per_day_amount_decimal = Decimal(cleaned_amount)
                        if per_day_amount_decimal <= 0:
                            errors['per_day_amount'] = ['Per day amount must be greater than 0']
                    except (ValueError, TypeError, decimal.InvalidOperation):
                        errors['per_day_amount'] = ['Please enter a valid per day amount (numbers only)']
                
                # Validate days
                if not days:
                    errors['days'] = ['Number of days is required']
                else:
                    try:
                        # Clean the days string - remove any non-numeric characters
                        cleaned_days = ''.join(c for c in days if c.isdigit())
                        if not cleaned_days:
                            raise ValueError("No numeric characters found")
                        
                        days_int = int(cleaned_days)
                        if days_int <= 0:
                            errors['days'] = ['Days must be greater than 0']
                    except (ValueError, TypeError):
                        errors['days'] = ['Please enter valid number of days (numbers only)']
                
                if errors:
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    })
                
                # Create charge
                charge = PaymentChargeDetail.objects.create(
                    payment=payment,
                    charge_type=charge_type,
                    description=description,
                    per_day_amount=per_day_amount_decimal,
                    days=days_int
                )
                charge.save()  # This will calculate total_amount via the save() method
                
                print(f"Charge created - ID: {charge.id}")  # Debug
                
                return JsonResponse({
                    'success': True,
                    'message': f'Charge added successfully! Total: ${charge.total_amount}',
                    'charge_id': charge.id,
                    'charge_data': {
                        'id': charge.id,
                        'charge_type': charge.get_charge_type_display(),  # This gives the human-readable version
                        'description': charge.description or '-',
                        'per_day_amount': str(charge.per_day_amount),
                        'days': charge.days,
                        'total_amount': str(charge.total_amount),
                        'created_at': charge.created_at.strftime('%b %d, %Y %I:%M %p')  # Format matches table
                    }
                })
                
        except Exception as e:
            import traceback
            print(f"Exception occurred: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'errors': {'general': [f'An error occurred: {str(e)}']}
            })
    
    return JsonResponse({
        'success': False,
        'errors': {'general': ['Invalid request method']}
    })

@login_required(login_url='login')
def delete_payment_charge(request):
    """Delete (soft delete) a payment charge"""
    if request.method == 'POST':
        try:
            charge_id = request.POST.get('charge_id')
            charge = get_object_or_404(PaymentChargeDetail, id=charge_id)
            
            # Soft delete
            charge.soft_delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Charge deleted successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,  
        'message': 'Invalid request method'
    })

@login_required(login_url='login')
def get_payment_charges(request, payment_id):
    """Get all charges for a payment"""
    try:
        payment = get_object_or_404(Payment_History, id=payment_id)
        charges = payment.charge_details.filter(deleted_at__isnull=True)
        
        charges_data = []
        for charge in charges:
            charges_data.append({
                'id': charge.id,
                'charge_type': charge.get_charge_type_display(),
                'description': charge.description,
                'per_day_amount': str(charge.per_day_amount),
                'days': charge.days,
                'total_amount': str(charge.total_amount),
                'created_at': charge.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'charges': charges_data,
            'total_charges': str(payment.total_charges_amount),
            'final_amount': str(payment.final_amount)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
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