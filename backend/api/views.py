# backend\api\views.py
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, time, timedelta
from rest_framework.pagination import PageNumberPagination
from django.db.models.functions import TruncDate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CategoryLotsSerializer, ContactMessageSerializer, LoginSerializer, WatchlistSerializer, CountrySerializer, CommentSerializer, PasswordUpdateSerializer,AuctionDetailSerializer, CategorySerializer, StateSerializer, CompanyListingSerializer, InventoryDetailSerializer, RegisterSerializer, ProfileUpdateSerializer, AuctionSerializer, PaymentHistorySerializer, InventorySerializerForSeller, BidHistorySerializerForSeller
from adminpanel.models import Group, Category, Watchlist, Country, State, Inventory, User, Comment, Profile, Auctions, Media, Payment_History, Company
from rest_framework import generics 
from django.utils import timezone
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.db.models import Max, Q, Prefetch
from django.utils.dateparse import parse_date
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework import generics
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from adminpanel.models import Inventory, Bid, Auctions
from decimal import Decimal
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import update_session_auth_hash



################################################################################################################
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            # Get user groups
            groups = list(user.groups.values_list('name', flat=True))

            return Response({
                "message": "Login successful",
                "authToken": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,  # Add user ID
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "groups": groups  # Include groups in response
                }
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            # This catches serializer validation errors
            return Response({
                "message": "Validation error",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Catch any other unexpected errors
            return Response({
                "message": "Login failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
################################################################################################################
class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            data = {
                'first_name': request.data.get('firstName'),
                'last_name': request.data.get('lastName'),
                'email': request.data.get('email'),
                'password': request.data.get('password'),
                'confirm_password': request.data.get('confirmPassword')
            }
            
            serializer = RegisterSerializer(data=data)
            
            if serializer.is_valid():
                user = serializer.save()

                # Assign "Buyer" group to the user
                try:
                    buyer_group = Group.objects.get(name="Buyer")
                    user.groups.add(buyer_group)
                except Group.DoesNotExist:
                    return Response({
                        "success": False,
                        "message": "Buyer group does not exist. Please create it in admin.",
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({
                    "success": True,
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "full_name": f"{user.first_name} {user.last_name}",
                        "date_joined": user.date_joined.isoformat()
                    }
                }, status=status.HTTP_201_CREATED)
            
            else:
                return Response({
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValidationError as e:
            return Response({
                "success": False,
                "message": "Password validation error",
                "errors": {"password": [str(e)]}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "success": False,
                "message": "Registration failed",
                "errors": {"general": [str(e)]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
################################################################################################################
class PasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        """Update user password"""
        try:
            serializer = PasswordUpdateSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                user = serializer.save()
                
                update_session_auth_hash(request, user)
                return Response({
                    "success": True,
                    "message": "Password updated successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "full_name": f"{user.first_name} {user.last_name}".strip(),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "success": False,
                "message": "Password update failed",
                "errors": {"general": [str(e)]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
################################################################################################################
class CountryListCreateView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CountryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
################################################################################################################
class StateListCreateView(generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer

class StateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
################################################################################################################
class StateByCountryView(generics.ListAPIView):
    serializer_class = StateSerializer

    def get_queryset(self):
        country_id = self.kwargs['country_id']
        return State.objects.filter(country__id=country_id)
################################################################################################################
class ProfileDetail(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        
        try:
            auth_user_data = User.objects.get(username=user.username)
            profile = Profile.objects.get(user=user)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        photo_url = request.build_absolute_uri(profile.photo.url) if profile.photo else None

        profile_data = {
            "user": {
                
                "username": auth_user_data.username,
                "email": auth_user_data.email,
                "first_name": auth_user_data.first_name,
                "last_name": auth_user_data.last_name,
                "title": profile.title,
                "phone_no": profile.phone_no,
                "gender": profile.gender,
                "address": profile.address,
                "country": profile.country.id if profile.country else None,
                "state": profile.state.id if profile.state else None,
                "city": profile.city,
                "zipcode": profile.zipcode,
                "photo": photo_url,
            },
        }

        return Response(profile_data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user = request.user
        try:
            auth_user_data = User.objects.get(username=user.username)
            profile = Profile.objects.get(user=user)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Extract User model fields from request data
        user_data = {}
        if 'first_name' in request.data:
            user_data['first_name'] = request.data.get('first_name')
        if 'last_name' in request.data:
            user_data['last_name'] = request.data.get('last_name')
        if 'email' in request.data:
            user_data['email'] = request.data.get('email')
            
        # Update User model if needed
        if user_data:
            # You may want to add validation here
            for key, value in user_data.items():
                setattr(auth_user_data, key, value)
            auth_user_data.save()

        # Deserialize the incoming data for updating Profile model
        profile_data = {k: v for k, v in request.data.items() 
                       if k in ['title', 'phone_no', 'gender', 'address', 'country', 'state', 'city', 'zipcode', 'photo']}
        
        serializer = ProfileUpdateSerializer(profile, data=profile_data, partial=True)        

        if serializer.is_valid():
            # Save the updated profile data
            serializer.save()

            photo_url = request.build_absolute_uri(profile.photo.url) if profile.photo else None

            # Respond with the updated profile data
            updated_profile_data = {
                "user": {                 
                    "username": auth_user_data.username,
                    "email": auth_user_data.email,
                    "first_name": auth_user_data.first_name,
                    "last_name": auth_user_data.last_name,
                    "title": serializer.validated_data.get('title', profile.title),
                    "phone_no": serializer.validated_data.get('phone_no', profile.phone_no),
                    "gender": serializer.validated_data.get('gender', profile.gender),
                    "address": serializer.validated_data.get('address', profile.address),
                    "country": serializer.validated_data.get('country', profile.country).id if serializer.validated_data.get('country', profile.country) else None,
                    "state": serializer.validated_data.get('state', profile.state).id if serializer.validated_data.get('state', profile.state) else None,
                    "city": serializer.validated_data.get('city', profile.city),
                    "zipcode": serializer.validated_data.get('zipcode', profile.zipcode),
                    "photo": photo_url,
                }
            }

            return Response(updated_profile_data, status=status.HTTP_200_OK)

        # If the data is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
################################################################################################################
class AuctionPagination(PageNumberPagination):
    """Custom pagination class for auctions"""
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to override page size
    max_page_size = 100  # Maximum page size limit

class AuctionListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AuctionSerializer
    pagination_class = AuctionPagination  # Add pagination class

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        auction_type = self.request.query_params.get('type', 'all')
        company_id = self.request.query_params.get('company_id')
        zip_code = self.request.query_params.get('distance_zip')  # Changed to match URL param
        radius_miles = self.request.query_params.get('distance_radius')
        # New closing date filter parameter
        closing_date = self.request.query_params.get('closing_date')

        queryset = Auctions.objects.select_related(
            'user__profile__company'
        ).all()

        # Filter by auction type
        if auction_type == 'featured':
            #queryset = queryset.filter(is_featured=True)
            queryset = queryset.filter(
                is_featured=True
            ).exclude(
                status__in=['closed', 'next']
            )
        elif auction_type == 'upcoming':
            queryset = queryset.filter(start_date__gt=now, status='next')
        elif auction_type == 'running':
            queryset = queryset.filter(status='current')
            
            # Alternative approach if you want to be more explicit:
            queryset = queryset.filter(
                Q(
                    # Prebid period: prebid started but main auction hasn't
                    Q(prebid_start_date__lte=now) & Q(start_date__gt=now)
                ) | Q(
                    # Main auction period: main auction has started but not ended
                    Q(start_date__lte=now) & (Q(end_date__isnull=True) | Q(end_date__gt=now))
                ),
                status='current'
            )

        # Filter by closing date
        if closing_date:
            try:
                # Parse the closing date string to a date object
                parsed_date = datetime.strptime(closing_date, '%Y-%m-%d').date()
                # Option 1: Compare dates in UTC (recommended)
                queryset = queryset.annotate(
                    end_date_utc=TruncDate('end_date', tzinfo=timezone.utc)
                ).filter(end_date_utc=parsed_date)
                
            except ValueError:
                raise ValidationError("Invalid closing date format. Use YYYY-MM-DD.")
            
        # Filter by company
        if company_id:
            queryset = queryset.filter(user__profile__company__id=company_id)

        # Radius filter
        if zip_code and radius_miles:
            try:
                geolocator = Nominatim(user_agent="auction_filter")
                ref_location = geolocator.geocode(zip_code) 

                if not ref_location:
                    raise ValidationError("Invalid ZIP code provided.")

                ref_coords = (ref_location.latitude, ref_location.longitude)
                radius_miles = float(radius_miles)

                filtered_queryset = []
                for auction in queryset:
                    # Determine source of lat/lng
                    if auction.seller_location == 'offsite':
                        lat = auction.latitude
                        lng = auction.longitude
                    else:
                        company = getattr(auction.user.profile, 'company', None)
                        lat = getattr(company, 'latitude', None)
                        lng = getattr(company, 'longitude', None)

                    if lat is not None and lng is not None:
                        distance = geodesic(ref_coords, (lat, lng)).miles
                        if distance <= radius_miles:
                            filtered_queryset.append(auction)

                return filtered_queryset

            except Exception as e:
                raise ValidationError(f"Geo lookup error: {str(e)}")

        return queryset

class ClosingSoonAuctionsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        now = timezone.now()

        auctions = Auctions.objects.filter(
            status='current',
            end_date__gt=now
        ).order_by('end_date').values('id', 'name', 'end_date')[:5]

        return Response(auctions)

################################################################################################################
# class AuctionDetailView(RetrieveAPIView):
#     queryset = Auctions.objects.select_related('user__profile__company').prefetch_related(
#         'inventory_set__category',
#         'inventory_set__media_items',
#         'inventory_set__bids'
#     ).all()
#     serializer_class = AuctionDetailSerializer  # Use the new serializer
#     permission_classes = [AllowAny]

#     def get_serializer_context(self):
#         """Pass request context to serializer for filtering"""
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         return context

#     def get_object(self):
#         """Custom sorting for bid-based sorting"""
#         obj = super().get_object()
#         sort_by = self.request.GET.get('sort_by')
        
#         if sort_by in ['lowest_bid', 'highest_bid']:
#             # Get inventory items and sort by current bid
#             inventory_items = list(obj.inventory_set.filter(deleted_at__isnull=True))
            
#             def get_current_bid(item):
#                 highest_bid = item.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
#                 return float(highest_bid.bid_amount) if highest_bid else float(item.starting_bid)
            
#             if sort_by == 'lowest_bid':
#                 inventory_items.sort(key=get_current_bid)
#             else:  # highest_bid
#                 inventory_items.sort(key=get_current_bid, reverse=True)
            
#             # Store sorted items on the object (this is a workaround)
#             obj._sorted_inventory = inventory_items
        
#         return obj
class AuctionDetailView(RetrieveAPIView):
    queryset = Auctions.objects.select_related('user__profile__company').prefetch_related(
        'inventory_set__category',
        'inventory_set__media_items',
        'inventory_set__bids'
    ).all()
    serializer_class = AuctionDetailSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        """Pass request context to serializer for filtering"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_object(self):
        """Custom sorting for bid-based sorting"""
        obj = super().get_object()
        sort_by = self.request.GET.get('sort_by')
        
        if sort_by in ['lowest_bid', 'highest_bid']:
            inventory_items = list(obj.inventory_set.filter(deleted_at__isnull=True))
            
            def get_current_bid(item):
                highest_bid = item.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
                return float(highest_bid.bid_amount) if highest_bid else float(item.starting_bid)
            
            if sort_by == 'lowest_bid':
                inventory_items.sort(key=get_current_bid)
            else:
                inventory_items.sort(key=get_current_bid, reverse=True)
            
            obj._sorted_inventory = inventory_items
        
        return obj
################################################################################################################
class InventoryDetailAPIView(RetrieveAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventoryDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
################################################################################################################
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_bid_api(request, lot_id):
    """
    API endpoint to place a bid on a lot
    """
    try:
        lot = Inventory.objects.get(id=lot_id, deleted_at__isnull=True)
        bid_amount = Decimal(str(request.data.get('amount', 0)))
        
        # Validate lot timing - Updated logic for pre-bids
        now = timezone.now()
        
        # Check if bidding has ended (this applies to both live bids and pre-bids)
        if lot.lot_end_time and lot.lot_end_time < now:
            return Response({
                'error': 'Bidding has ended for this lot'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine bid type based on timing
        bid_type = 'Pre Bid'  # Default to pre-bid
        
        if lot.lot_start_time and lot.lot_start_time <= now:
            # Lot has started, this is a live bid
            bid_type = 'Live Bid'
        elif lot.lot_start_time and lot.lot_start_time > now:
            # Lot hasn't started yet, this is a pre-bid (allowed)
            bid_type = 'Pre Bid'
        
        # Get current highest bid
        latest_bid = lot.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        current_bid = latest_bid.bid_amount if latest_bid else lot.starting_bid
        required_bid = current_bid + lot.auction.bid_increment
        
        if bid_amount < required_bid:
            return Response({
                'error': f'Bid must be at least ₹{required_bid}',
                'required_bid': str(required_bid)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create bid with appropriate type
        bid = Bid.objects.create(
            user=request.user,
            auction=lot.auction,
            inventory=lot,
            bid_amount=bid_amount,
            type=bid_type  # Use determined bid type
        )
        
        # Check if reserve is met
        reserve_met = bid_amount >= lot.reserve_price
        was_reserve_met_before = current_bid >= lot.reserve_price
        
        # Send WebSocket notification
        channel_layer = get_channel_layer()
        room_group_name = f'lot_{lot_id}'
        
        # Broadcast bid placed
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'bid_placed',
                'bid_data': {
                    'bidder': request.user.username,
                    'amount': str(bid_amount),
                    'timestamp': bid.created_at.isoformat(),
                    'reserve_met': reserve_met,
                    'next_required_bid': str(bid_amount + lot.auction.bid_increment),
                    'bid_type': bid_type
                }
            }
        )
        
        # Send reserve met notification if applicable
        if reserve_met and not was_reserve_met_before:
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'reserve_met',
                    'data': {
                        'lot_id': lot_id,
                        'reserve_price': str(lot.reserve_price)
                    }
                }
            )
        
        return Response({
            'success': True,
            'bid': {
                'id': bid.id,
                'amount': str(bid.bid_amount),
                'timestamp': bid.created_at.isoformat(),
                'bidder': request.user.username,
                'type': bid_type
            },
            'lot_status': {
                'current_bid': str(bid_amount),
                'next_required_bid': str(bid_amount + lot.auction.bid_increment),
                'reserve_met': reserve_met
            }
        }, status=status.HTTP_201_CREATED)
        
    except Inventory.DoesNotExist:
        return Response({
            'error': 'Lot not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
################################################################################################################    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bid_history(request, lot_id):
    """
    Get bid history for a specific lot
    """
    try:
        lot = Inventory.objects.get(id=lot_id, deleted_at__isnull=True)
        bids = lot.bids.filter(deleted_at__isnull=True).order_by('-created_at')
        
        bid_history = [
            {
                'id': bid.id,
                'bidder': bid.user.username,
                'amount': str(bid.bid_amount),
                'timestamp': bid.created_at.isoformat(),
                'is_current_user': bid.user == request.user
            } for bid in bids
        ]
        
        return Response({
            'bid_history': bid_history,
            'total_bids': len(bid_history)
        }, status=status.HTTP_200_OK)
        
    except Inventory.DoesNotExist:
        return Response({
            'error': 'Lot not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
################################################################################################################
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lot_status(request, lot_id):
    """
    Get current status of a lot including current bid, next required bid, etc.
    """
    try:
        lot = Inventory.objects.get(id=lot_id, deleted_at__isnull=True)
        latest_bid = lot.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        current_bid = latest_bid.bid_amount if latest_bid else lot.starting_bid
        
        return Response({
            'lot_id': lot.id,
            'title': lot.title,
            'current_bid': str(current_bid),
            'next_required_bid': str(current_bid + lot.auction.bid_increment),
            'high_bidder': latest_bid.user.username if latest_bid else None,
            'reserve_met': current_bid >= lot.reserve_price,
            'reserve_price': str(lot.reserve_price),
            'starting_bid': str(lot.starting_bid),
            'bid_increment': str(lot.auction.bid_increment),
            'lot_start_time': lot.lot_start_time.isoformat() if lot.lot_start_time else None,
            'lot_end_time': lot.lot_end_time.isoformat() if lot.lot_end_time else None,
            'is_active': (
                lot.lot_start_time <= timezone.now() <= lot.lot_end_time 
                if lot.lot_start_time and lot.lot_end_time else False
            )
        }, status=status.HTTP_200_OK)
        
    except Inventory.DoesNotExist:
        return Response({
            'error': 'Lot not found'
        }, status=status.HTTP_404_NOT_FOUND)
################################################################################################################
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bidding_history(request):
    """
    Get user's bidding history with 4 tabs: All Bids, Won Bids, Lost Bids, Active Bids
    """
    try:
        user = request.user
        tab = request.query_params.get('tab', 'all')  # all, won, lost, active
        now = timezone.now()

        # Get all relevant bids for the user
        user_bids = Bid.objects.filter(
            user=user,
            deleted_at__isnull=True
        ).select_related('inventory', 'auction') \
         .prefetch_related('inventory__media_items') \
         .order_by('-created_at')

        # Optional: auction filter
        auction_id = request.query_params.get('auction_id')
        if auction_id:
            user_bids = user_bids.filter(auction_id=auction_id)

        seen_keys = set()
        bidding_history = []

        for bid in user_bids:
            key = (bid.inventory_id, bid.auction_id)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            inventory = bid.inventory
            auction = bid.auction

            # Fetch all bids for this inventory in this auction
            all_bids = Bid.objects.filter(
                inventory=inventory,
                auction=auction,
                deleted_at__isnull=True
            ).order_by('-bid_amount')

            highest_bid = all_bids.first()
            user_last_bid = Bid.objects.filter(
                user=user,
                inventory=inventory,
                auction=auction,
                deleted_at__isnull=True
            ).order_by('-created_at').first()

            is_lot_active = inventory.lot_end_time and inventory.lot_end_time > now
            is_reserve_met = highest_bid and highest_bid.bid_amount >= inventory.reserve_price
            reserve_met = is_reserve_met
            # Only mark as 'won' if auction ended AND user is highest bidder AND reserve met
            is_winner = (
                not is_lot_active and
                highest_bid and
                highest_bid.user == user and
                is_reserve_met
            )


            bid_status = (
                'active' if is_lot_active  else
                'won' if is_winner else
                'lost'
            )

            current_bid = highest_bid.bid_amount if highest_bid else inventory.starting_bid
            reserve_met = current_bid >= inventory.reserve_price

            first_image = None
            first_media = inventory.media_items.first()
            if first_media:
                if hasattr(first_media, 'media_file') and first_media.media_file:
                    first_image = request.build_absolute_uri(first_media.media_file.url)
                elif hasattr(first_media, 'path') and first_media.path:
                    first_image = first_media.path

            history_item = {
                'inventory_id': inventory.id,
                'inventory_title': inventory.title,
                'inventory_first_image': first_image,
                'auction_id': auction.id,
                'auction_name': auction.name,
                'highest_bid': str(highest_bid.bid_amount) if highest_bid else str(inventory.starting_bid),
                'my_last_bid': str(user_last_bid.bid_amount) if user_last_bid else None,
                'lot_end_time': inventory.lot_end_time,
                'bid_status': bid_status,
                'is_winning': is_winner,
                'reserve_met': reserve_met,
                'total_bids_by_me': Bid.objects.filter(
                    user=user, inventory=inventory, auction=auction, deleted_at__isnull=True
                ).count(),
                'last_bid_time': user_last_bid.created_at if user_last_bid else None,
                'starting_bid': str(inventory.starting_bid),
                'reserve_price': str(inventory.reserve_price),
                'winning_user_id': highest_bid.user.id if not is_auction_active and highest_bid else None,
                'winning_bid_amount': str(highest_bid.bid_amount) if highest_bid else None,
            }

            bidding_history.append(history_item)

        # Sort by last bid time
        bidding_history.sort(key=lambda x: x['last_bid_time'] or timezone.datetime.min.replace(tzinfo=timezone.utc), reverse=True)

        # Tab filters
        all_items = bidding_history.copy()
        won_items = [item for item in all_items if item['bid_status'] == 'won']
        lost_items = [item for item in all_items if item['bid_status'] == 'lost']
        active_items = [item for item in all_items if item['bid_status'] == 'active']

        if tab == 'won':
            bidding_history = won_items
        elif tab == 'lost':
            bidding_history = lost_items
        elif tab == 'active':
            bidding_history = active_items
        # else 'all' => no filtering

        return Response({
            'success': True,
            'data': bidding_history,
            'counts': {
                'all': len(all_items),
                'won': len(won_items),
                'lost': len(lost_items),
                'active': len(active_items)
            },
            'current_tab': tab,
            'total_items': len(bidding_history)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################################################################################################
#PAYMENT HISTORY FOR PARTICULER USERS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_payment_history(request):
    """
    Get user's payment history with 3 tabs: All, Pending, Paid
    """
    try:
        user = request.user
        tab = request.query_params.get('tab', 'all')  # all, pending, paid
        
        # Get all payment histories for the user
        payment_histories = Payment_History.objects.filter(
            user=user,
            deleted_at__isnull=True
        ).select_related(
            'inventory__auction',
            'inventory__category'
        ).prefetch_related(
            Prefetch('inventory__media_items', queryset=Media.objects.all())
        ).order_by('-created_at')
        
        # Organize payment data
        payment_data = []
        
        for payment in payment_histories:
            # Get first image of the lot
            first_image = None
            if payment.inventory:
                first_media = payment.inventory.media_items.first()
                if first_media:
                    if hasattr(first_media, 'media_file') and first_media.media_file:
                        first_image = request.build_absolute_uri(first_media.media_file.url)
                    elif hasattr(first_media, 'path') and first_media.path:
                        first_image = first_media.path
            
            # Determine payment status for filtering
            payment_status_filter = None
            if payment.status == Payment_History.PaymentStatus.PENDING:
                payment_status_filter = 'pending'
            elif payment.status in [Payment_History.PaymentStatus.COMPLETED]:
                payment_status_filter = 'paid'
            elif payment.status in [Payment_History.PaymentStatus.FAILED, Payment_History.PaymentStatus.REFUNDED]:
                payment_status_filter = 'failed'  # You can adjust this logic as needed
            
            payment_item = {
                'payment_id': payment.id,
                'transaction_id': payment.transaction_id,
                'lot_name': payment.inventory.title if payment.inventory else None,
                'lot_image': first_image,
                'lot_id': payment.inventory.id if payment.inventory else None,
                'auction_name': payment.inventory.auction.name if payment.inventory and payment.inventory.auction else None,
                'auction_id': payment.inventory.auction.id if payment.inventory and payment.inventory.auction else None,
                'price': str(payment.amount),
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'payment_method': payment.payment_method,
                'payment_method_display': payment.get_payment_method_display(),
                'date': payment.created_at,
                'updated_date': payment.updated_at,
                'payment_status_filter': payment_status_filter,
                # Additional useful fields
                'inventory_number': payment.inventory.inventory_number if payment.inventory else None,
                'lot_condition': payment.inventory.condition if payment.inventory else None,
            }
            
            payment_data.append(payment_item)
        
        # Calculate counts for all tabs
        all_payments = payment_data.copy()
        pending_payments = [item for item in all_payments if item['payment_status_filter'] == 'pending']
        paid_payments = [item for item in all_payments if item['payment_status_filter'] == 'paid']
        
        # Filter based on tab
        if tab == 'pending':
            filtered_payments = pending_payments
        elif tab == 'paid':
            filtered_payments = paid_payments
        else:  # all
            filtered_payments = all_payments
        
        return Response({
            'success': True,
            'data': filtered_payments,
            'counts': {
                'all': len(all_payments),
                'pending': len(pending_payments),
                'paid': len(paid_payments)
            },
            'current_tab': tab,
            'total_items': len(filtered_payments)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
################################################################################################################   
class CompanyListView(generics.ListAPIView):
    """List all companies with state and country information"""
    #permission_classes = [permissions.AllowAny]  # Change as needed
    serializer_class = CompanyListingSerializer
    
    def get_queryset(self):
        """Get companies with related country and state data"""
        queryset = Company.objects.select_related('country', 'state').all()
        
        # Optional filtering parameters
        country_id = self.request.query_params.get('country_id')
        state_id = self.request.query_params.get('state_id')
        city = self.request.query_params.get('city')
        search = self.request.query_params.get('search')
        
        # Filter by country
        if country_id:
            queryset = queryset.filter(country_id=country_id)
            
        # Filter by state
        if state_id:
            queryset = queryset.filter(state_id=state_id)
            
        # Filter by city
        if city:
            queryset = queryset.filter(city__icontains=city)
            
        # Search by company name
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(city__icontains=search) |
                Q(country__name__icontains=search) |
                Q(state__name__icontains=search)
            )
        
        return queryset.order_by('name')   
################################################################################################################
class CategoryListView(APIView):
    def get(self, request):
        # Get only top-level categories (assuming top-level has no parent)
        categories = Category.objects.filter(parent__isnull=True, deleted_at__isnull=True).order_by('order')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryLotsView(generics.ListAPIView):
    """Updated view for category-based lot listing with optional category filtering"""
    permission_classes = [AllowAny]
    serializer_class = CategoryLotsSerializer

    def get_queryset(self):
        return [{}]  # Dummy queryset since we handle data in serializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['category_id'] = self.request.GET.get('category_id')
        return context

    def list(self, request, *args, **kwargs):
        category_id = request.GET.get('category_id', '').strip()
        
        # If category_id is provided and not empty, validate it exists
        if category_id:
            # Handle comma-separated category IDs
            category_ids = [id.strip() for id in category_id.split(',') if id.strip()]
            
            if category_ids:
                try:
                    # Validate that all category IDs exist
                    for cat_id in category_ids:
                        int(cat_id)  # Check if it's a valid integer
                        Category.objects.get(id=int(cat_id), deleted_at__isnull=True)  # Check if category exists and not deleted
                except (Category.DoesNotExist, ValueError):
                    return Response({'error': 'One or more categories not found'}, status=404)
        
        # If no category_id or empty category_id, fetch all lots
        # This allows the API to work with or without category filtering
        
        serializer = self.get_serializer({})
        return Response(serializer.data)
#######################################
class ContactFormView(APIView):
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # # Send email            data = serializer.validated_data
            # send_mail(
            #     subject=f"New Contact: {data['subject']}",
            #     message=f"From: {data['name']} <{data['email']}>\n\n{data['message']}",
            #     from_email='your_email@example.com',
            #     recipient_list=['your_email@example.com'],
            #     fail_silently=False            )

            return Response({'message': 'Message received and email sent!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger(__name__)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_invoice(request, payment_id):
    """
    Download invoice PDF for a specific payment
    """
    try:
        # Get the payment with related data (simplified query)
        payment = Payment_History.objects.select_related(
            'user',
            'user__profile',
            'inventory',
            'inventory__auction'
        ).prefetch_related(
            'charge_details'
        ).get(id=payment_id, user=request.user)

        # Calculate buyer's premium (5% of the amount)
        buyers_premium = (payment.amount * 5) / 100  # 5% buyers premium

        # Get all payment charges (excluding soft-deleted ones if applicable)
        payment_charges = payment.charge_details.all()
        if hasattr(payment_charges, 'filter'):
            payment_charges = payment_charges.filter(deleted_at__isnull=True) if hasattr(payment_charges.model, 'deleted_at') else payment_charges.all()
        total_charges = sum([charge.total_amount for charge in payment_charges])

        # Calculate grand total
        grand_total = payment.amount + buyers_premium + total_charges

        # Prepare context for the template
        context = {
            'payment': payment,
            'buyers_premium': buyers_premium,
            'payment_charges': payment_charges,
            'total_charges': total_charges,
            'grand_total': grand_total,
            'MEDIA_URL': settings.MEDIA_URL,
        }

        # Render HTML template
        html = render_to_string('payments/invoice.html', context)

        # Create PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            response = HttpResponse(
                result.getvalue(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="invoice_{payment_id}.pdf"'
            )
            return response
        else:
            logger.error(f"PDF generation error: {pdf.err}")
            return HttpResponse(
                'Error generating PDF',
                status=500,
                content_type='text/plain'
            )

    except Payment_History.DoesNotExist:
        return HttpResponse(
            'Payment not found or access denied',
            status=404,
            content_type='text/plain'
        )
    except Exception as e:
        logger.error(f"Error generating invoice: {str(e)}")
        return HttpResponse(
            'Internal server error',
            status=500,
            content_type='text/plain'
        )
################################################################################
class WatchlistAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WatchlistSerializer

    def get(self, request):
        """List all watchlist items for the current user"""
        watchlist = Watchlist.objects.filter(user=request.user).select_related('inventory')
        serializer = self.get_serializer(watchlist, many=True)
        return Response(serializer.data)

    def post(self, request, inventory_id=None):
        """Add an item to watchlist (inventory_id in URL)"""
        if not inventory_id:
            return Response(
                {'error': 'inventory_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inventory = get_object_or_404(Inventory, id=inventory_id)
        
        if Watchlist.objects.filter(user=request.user, inventory=inventory).exists():
            return Response(
                {'error': 'Item already in watchlist'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        watchlist_item = Watchlist.objects.create(user=request.user, inventory=inventory)
        serializer = self.get_serializer(watchlist_item)
        return Response({
            'message': 'Item added to watchlist',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, inventory_id=None):
        """Remove an item from watchlist (inventory_id in URL)"""
        if not inventory_id:
            return Response(
                {'error': 'inventory_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        watchlist_item = get_object_or_404(
            Watchlist, 
            user=request.user, 
            inventory__id=inventory_id
        )
        watchlist_item.delete()
        return Response(
            {'message': 'Item removed from watchlist'}, 
            status=status.HTTP_200_OK
        )
#######################################################################    
class LotCommentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lot_id):
        """Get all comments for a specific lot"""
        try:
            # Get the inventory item (lot)
            inventory = get_object_or_404(Inventory, id=lot_id)
            
            # Get all comments for this lot
            comments = Comment.objects.filter(inventory=inventory)
            serializer = CommentSerializer(comments, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, lot_id):
        """Add a new comment to a specific lot"""
        try:
            # Get the inventory item (lot)
            inventory = get_object_or_404(Inventory, id=lot_id)
            
            # Get the auction from the inventory
            auction = inventory.auction
            
            # Get comment text from request
            content = request.data.get('text') or request.data.get('content')
            
            if not content:
                return Response(
                    {'error': 'Comment text is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the comment
            comment = Comment.objects.create(
                auction=auction,
                inventory=inventory,
                user=request.user,
                content=content
            )
            
            # Serialize and return the comment
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Inventory.DoesNotExist:
            return Response(
                {'error': 'Lot not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
################################################################################################################
# SELLER DASHBORD #
################################################################################################################          
@api_view(['GET'])
def seller_inventory(request, seller_id):
    # Get all inventory items from auctions created by this seller
    inventory = Inventory.objects.filter(
        auction__user_id=seller_id
    ).select_related('auction', 'winning_user')
    
    serializer = InventorySerializerForSeller(inventory, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def item_bid_history(request, item_id):
    # Get bid history for a specific inventory item
    bids = Bid.objects.filter(inventory_id=item_id).order_by('-created_at')
    serializer = BidHistorySerializerForSeller(bids, many=True)
    return Response(serializer.data)