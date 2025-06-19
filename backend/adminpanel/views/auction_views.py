from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.utils import IntegrityError
from adminpanel.models import Auctions
from adminpanel.forms import AuctionForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from adminpanel.utils import get_coordinates_from_address  # import at top

from adminpanel.models import Inventory, Country
#All Auction
@login_required(login_url='login')
def all_auctions(request, tabId):
    current_date = timezone.now()

    # Fetch auctions based on their status
    running_auctions = Auctions.objects.filter(
        status='current'
    ).order_by('-created_at', 'state__name')  # Sort by state and created_at

    upcoming_auctions = Auctions.objects.filter(
        status='next'
    ).order_by('-created_at', 'state__name')  # Sort by state and created_at

    closed_auctions = Auctions.objects.filter(
        status='closed'
    ).order_by('-created_at', 'state__name')  # Sort by state and created_at

    context = {
        'running_auctions': running_auctions,
        'upcoming_auctions': upcoming_auctions,
        'closed_auctions': closed_auctions,
        'tabId': tabId,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'auctions/index.html', context)

# Create Auction
@login_required(login_url='login')
@csrf_exempt
def create_auction(request):
    # Get the "Sellers" group
    sellers_group = Group.objects.get(name='Seller')
    countries = Country.objects.prefetch_related('states').all()

    # Filter users who are in the "Sellers" group
    users = User.objects.filter(groups=sellers_group)

    if request.method == 'POST':
        form = AuctionForm(request.POST)

        if form.is_valid():
            auction = form.save(commit=False)  # Don't save to DB yet

            # Get the selected user from the form
            auction.user = form.cleaned_data['user']  # Correctly assign the user instance

            if auction.seller_location == 'offsite':
                address_parts = [
                    auction.address,
                    auction.city,
                    auction.state.name if auction.state else '',
                    auction.country.name if auction.country else '',
                    auction.zipcode
                ]
                full_address = ', '.join(filter(None, address_parts))
                lat, lng = get_coordinates_from_address(full_address)
                auction.latitude = lat
                auction.longitude = lng
            elif auction.seller_location == 'onsite' and auction.user and hasattr(auction.user, 'profile') and auction.user.profile.company:
                # If seller is onsite, copy from the company
                company = auction.user.profile.company
                auction.latitude = company.latitude
                auction.longitude = company.longitude

            try:
                auction.save()  # Now save the auction
                return JsonResponse({'success': True, 'message': 'Auction Created successfully.'})
            except Exception as e:
                return JsonResponse({'errors': 'error', 'message': str(e)}, status=400)

        else:
            return JsonResponse({'errors': 'error', 'errors': form.errors}, status=400)
    else:
        form = AuctionForm()
        return render(request, 'auctions/create.html', {'form': form, 'users': users, 'countries': countries})

# Edit Auction
@login_required(login_url='login')
@csrf_exempt
def edit_auction(request, auction_id):
    tabId = request.GET.get('tabId', 1)   
    countries = Country.objects.prefetch_related('states').all()

    # Get the auction object or return a 404 if not found
    auction = get_object_or_404(Auctions, id=auction_id)
    try:
        # Get the "Sellers" group
        sellers_group = Group.objects.get(name='Seller')
        # Filter users who are in the "Sellers" group
        users = User.objects.filter(groups=sellers_group)
    except Group.DoesNotExist:
        users = User.objects.none()

    if request.method == 'POST':
        form = AuctionForm(request.POST, instance=auction)  # Pass the instance to pre-fill

        if form.is_valid():
            auction = form.save(commit=False)  # Don't save to DB yet
            auction.user = form.cleaned_data['user']  # Set the user if needed

            if auction.seller_location == 'offsite':
                address_parts = [
                    auction.address,
                    auction.city,
                    auction.state.name if auction.state else '',
                    auction.country.name if auction.country else '',
                    auction.zipcode
                ]
                full_address = ', '.join(filter(None, address_parts))
                lat, lng = get_coordinates_from_address(full_address)
                auction.latitude = lat
                auction.longitude = lng

            elif auction.seller_location == 'onsite' and auction.user and hasattr(auction.user, 'profile') and auction.user.profile.company:
                company = auction.user.profile.company
                auction.latitude = company.latitude
                auction.longitude = company.longitude

            try:
                auction.save()  
                return JsonResponse({'success': True, 'message': 'Auction updated successfully.'})
            except Exception as e:
                return JsonResponse({'errors': 'error', 'message': str(e)}, status=400)

        else:
            return JsonResponse({'errors': 'error', 'errors': form.errors}, status=400)
    else:
        form = AuctionForm(instance=auction)  # Pre-fill the form with the auction instance
        return render(request, 'auctions/edit.html', {'tabId':tabId, 'form': form, 'users': users, 'auction': auction, 'countries': countries})

# Auction Delete
@login_required(login_url='login')
def delete_auction(request):
    auctionId = request.POST.get('auctionId')
    auction = get_object_or_404(Auctions, id=auctionId)
    try:
        auction.delete()
        return JsonResponse({'status': 'success', 'message': 'Item has been deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'There was an error deleting the item.'})

@require_POST
@login_required(login_url='login')
def transfer_inventory(request):
    inventory_ids = request.POST.getlist('inventory_ids')
    auction_id = request.POST.get('auction_id')

    if not inventory_ids or not auction_id:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    try:
        auction = Auctions.objects.get(id=auction_id)
        inventory_items = Inventory.objects.filter(id__in=inventory_ids)

        already_assigned = []
        updated_status = []
        newly_assigned = []

        for inventory in inventory_items:
            if inventory.auction_id == auction.id:
                if inventory.status != 'auction':
                    inventory.status = 'auction'
                    inventory.save(update_fields=['status'])
                    updated_status.append(inventory.id)
                already_assigned.append(inventory.id)
            else:
                inventory.auction = auction
                inventory.status = 'auction'
                inventory.save(update_fields=['auction', 'status'])
                newly_assigned.append(inventory.id)

        # Construct message
        if newly_assigned or updated_status:
            if already_assigned:
                message = 'Some items were already assigned to the auction, but their statuses were updated if needed. New items were added successfully.'
            else:
                message = 'All selected items were successfully transferred and statuses updated.'
        else:
            message = 'All selected items were already assigned to the selected auction with correct status.'

        return JsonResponse({'status': 'success', 'message': message})

    except Auctions.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Auction does not exist'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required(login_url='login')
def auction_inventory(request):
    auction_id = request.GET.get('auctionId')
    auction = Auctions.objects.get(id=auction_id)
    inventorys = auction.inventory_set.all()

    inventory_list = []
    for inventory in inventorys:
        first_image = inventory.media_items.filter(type='IMAGE').first()
        item_dict = {
            'id': inventory.id,
            'name': inventory.title,  # Change this to `title`, assuming `name` is incorrect
            'status': inventory.status,
            'starting_bid_amount': inventory.starting_bid, 
            'reserve_price': inventory.reserve_price, # Correct field
            'first_image_url': first_image.path if first_image else '',
        }
        inventory_list.append(item_dict)

    return JsonResponse({
        'status': 'success',
        'auction_status': auction.status, 
        'inventory_list': inventory_list
    })

@login_required(login_url='login')
def remove_inventory_from_auction(request):
    if request.method == 'POST':
        inventory_id = request.POST.get('InventoryId')  # Match the POST key used in AJAX
        try:
            # Fetch the inventory item
            inventory = Inventory.objects.get(id=inventory_id)

            # Remove the inventory from auction and set its status to "pending"
            inventory.auction = None
            inventory.status = 'pending'
            inventory.save()

            return JsonResponse({'status': 'success'})
        except Inventory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item does not exist'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def get_company_details(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'No user_id provided'}, status=400)

    user = get_object_or_404(User, pk=user_id)
    
    # Get the related profile
    profile = getattr(user, 'profile', None)
    if not profile:
        return JsonResponse({'error': 'Profile not found for this user'}, status=404)

    company = profile.company
    if not company:
        return JsonResponse({'error': 'Company not linked with this user'}, status=404)

    return JsonResponse({
        'company_name': company.name,
        'address': company.address,
        'phone_no': company.phone_no,
        'city': company.city,
        'zipcode': company.zipcode,
        'country': company.country.name if company.country else None,
        'state': company.state.name if company.state else None,
        'company_logo_url': company.company_logo.url if company.company_logo else None,
    })