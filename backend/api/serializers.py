# backend\api\serializers.py
from decimal import Decimal
import re
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth.models import User
from adminpanel.models import Country, State, Media, Inventory, Profile, Auctions, Company, Comment, Category, Bid, Payment_History, Watchlist, PaymentChargeDetail, ContactMessage
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.db import models
from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from rest_framework import serializers
from adminpanel.models import Inventory, Category
from social_core.exceptions import AuthForbidden
from google.oauth2 import id_token

################################################################################################################
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Check if the email is registered
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                _("Email not registered."),
                code='not_registered'
            )

        # Authenticate the user using email and password
        user = authenticate(username=user.username, password=password)
        
        if not user:
            raise serializers.ValidationError(
                _("Your password is incorrect. Please reset if you don't remember it."),
                code='wrong_password'
            )

        attrs['user'] = user
        return attrs   
################################################################################################################
class PasswordUpdateSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(required=True, write_only=True)
    newPassword = serializers.CharField(required=True, write_only=True)
    confirmNewPassword = serializers.CharField(required=True, write_only=True)
 
    def validate_currentPassword(self, value):
        """Validate current password against database"""
        user = self.context['request'].user
        
        # Check password against database
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
 
    def validate_newPassword(self, value):
        """Validate new password strength"""
        if not value:
            raise serializers.ValidationError("New password is required.")
        
        # Length check
        if len(value) < 8:
            raise serializers.ValidationError("New password must be at least 8 characters long.")
        
        # Uppercase check
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("New password must contain at least one uppercase letter.")
        
        # Lowercase check
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("New password must contain at least one lowercase letter.")
        
        # Digit check
        if not re.search(r'\d', value):
            raise serializers.ValidationError("New password must contain at least one digit.")
        
        # Special character check
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("New password must contain at least one special character.")
        
        return value
 
    def validate(self, attrs):
        """Cross-field validation"""
        current_password = attrs.get('currentPassword')
        new_password = attrs.get('newPassword')
        confirm_new_password = attrs.get('confirmNewPassword')
        
        # Check if passwords match
        if new_password != confirm_new_password:
            raise serializers.ValidationError({
                "confirmNewPassword": "New passwords do not match."
            })
        
        # Check if new password is different from current
        if current_password == new_password:
            raise serializers.ValidationError({
                "newPassword": "New password must be different from current password."
            })
        
        return attrs
 
    def save(self):
        """Save new password to database"""
        user = self.context['request'].user
        new_password = self.validated_data['newPassword']
        
        # Set and save new password (this will hash it automatically)
        user.set_password(new_password)
        user.save()
        
        return user
################################################################################################################
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
 
    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']
 
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
 
    def validate_first_name(self, value):
        """Validate first name"""
        if not value.strip():
            raise serializers.ValidationError("First name cannot be empty.")
        return value.strip()
 
    def validate_last_name(self, value):
        """Validate last name"""
        if not value.strip():
            raise serializers.ValidationError("Last name cannot be empty.")
        return value.strip()
 
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs
 
    def generate_unique_username(self, first_name, last_name):
        """Generate a unique username from first and last name"""
        first_clean = re.sub(r'[^a-zA-Z0-9]', '', first_name).lower()
        last_clean = re.sub(r'[^a-zA-Z0-9]', '', last_name).lower()
        base_username = f"{first_clean}_{last_clean}"
        
        if len(base_username) < 4:
            base_username = (first_clean[:3] + last_clean[:3]).ljust(4, '0')
        
        base_username = base_username[:30]
        
        if not User.objects.filter(username=base_username).exists():
            return base_username
        
        counter = 1
        while True:
            new_username = f"{base_username[:27]}{counter:03d}"
            if not User.objects.filter(username=new_username).exists():
                return new_username
            counter += 1
            
            if counter > 999:
                import time
                email_prefix = attrs.get('email', '').split('@')[0][:20]
                timestamp = str(int(time.time()))[-6:]
                return f"{email_prefix}_{timestamp}"
 
    def create(self, validated_data):
        """Create user with auto-generated username"""
        validated_data.pop('confirm_password')
        username = self.generate_unique_username(
            validated_data['first_name'],
            validated_data['last_name']
        )
        
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        
        return user 
################################################################################################################

################################################################################################################
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories', 'order','image']

    def get_subcategories(self, obj):
        children = obj.subcategories.filter(deleted_at__isnull=True, is_active=True).order_by('order')
        return CategorySerializer(children, many=True).data
################################################################################################################
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
################################################################################################################
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'
################################################################################################################
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'  
################################################################################################################
class InventorySerializer(serializers.ModelSerializer):
    media_items = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    current_bid = serializers.SerializerMethodField()
    next_required_bid = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = '__all__' 

    def get_current_bid(self, obj):
        highest_bid = obj.bids.filter(
            deleted_at__isnull=True,
            auction=obj.auction
        ).order_by('-bid_amount').first()
        return str(highest_bid.bid_amount) if highest_bid else str(obj.starting_bid)
    
    def get_current_highest_bid(self, obj):
        # Get the highest bid for this inventory item
        highest_bid = obj.bids.filter(
            deleted_at__isnull=True,
            auction=obj.auction
        ).order_by('-bid_amount').first()
        return highest_bid
    
    def get_next_required_bid(self, obj):
        current_highest_bid = self.get_current_highest_bid(obj)
        if current_highest_bid is None:
            # Handle case where there are no bids yet
            if obj.starting_bid is None:
                return None  # or some default value
            return obj.starting_bid
        
        # Make sure bid_increment exists before accessing it
        if not hasattr(obj, 'bid_increment') or obj.bid_increment is None:
            return Decimal(current_highest_bid.bid_amount) + Decimal('1.00')  # default increment
            
        return Decimal(current_highest_bid.bid_amount) + Decimal(str(obj.bid_increment))
################################################################################################################
class ProfileSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    state = StateSerializer()

    class Meta:
        model = Profile
        fields = ['title','phone_no', 'gender', 'address', 'country', 'state', 'city', 'zipcode', 'photo']
################################################################################################################
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        read_only_fields = ['username']
################################################################################################################
class ProfileDetailSerializer(serializers.Serializer):
    auth_user = UserSerializer()
    profile = ProfileSerializer()
################################################################################################################    
class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    
    class Meta:
        model = Profile
        fields = ['title', 'phone_no', 'gender', 'address', 'country', 'state', 'city', 'zipcode', 
                 'first_name', 'last_name', 'email', 'photo']
    
    def update(self, instance, validated_data):
        # Extract user data if present
        user_data = validated_data.pop('user', {})
        
        # Update user data if present
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
            
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
################################################################################################################
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'phone_no', 'company_logo']
################################################################################################################
class AuctionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    location_details = serializers.SerializerMethodField()
    inventory_items = serializers.SerializerMethodField()
    lot_count = serializers.SerializerMethodField()   

    class Meta:
        model = Auctions
        fields = '__all__'

    def get_location_details(self, obj):
        if obj.seller_location == 'onsite':
            try:
                company = obj.user.profile.company
                if company:
                    return {
                        'address': company.address,
                        'country': company.country.name if company.country else None,
                        'state': company.state.name if company.state else None,
                        'city': company.city,
                        'zipcode': company.zipcode,
                        'name': company.name,
                        'phone_no': company.phone_no,
                        'company_logo': company.company_logo.url if company.company_logo else None,
                    }
            except Exception:
                return {}
        elif obj.seller_location == 'offsite':
            return {
                'address': obj.address,
                'country': obj.country.name if obj.country else None,
                'state': obj.state.name if obj.state else None,
                'city': obj.city,
                'zipcode': obj.zipcode,
            }
        return {}

    def get_inventory_items(self, obj):
        # Only active inventory (not soft-deleted)
        inventory = obj.inventory_set.filter(deleted_at__isnull=True)
        return InventorySerializer(inventory, many=True).data
    def get_lot_count(self, obj):
        return obj.inventory_set.filter(deleted_at__isnull=True).count()
################################################################################################################
class AuctionDetailSerializer(serializers.ModelSerializer):
    """Enhanced serializer for auction details with filtering support"""
    user = UserSerializer(read_only=True)
    location_details = serializers.SerializerMethodField()
    inventory_items = serializers.SerializerMethodField()
    lot_count = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    bid_range = serializers.SerializerMethodField()

    class Meta:
        model = Auctions
        fields = '__all__'

    def get_location_details(self, obj):
        if obj.seller_location == 'onsite':
            try:
                company = obj.user.profile.company
                if company:
                    return {
                        'address': company.address,
                        'country': company.country.name if company.country else None,
                        'state': company.state.name if company.state else None,
                        'city': company.city,
                        'zipcode': company.zipcode,
                        'name': company.name,
                        'phone_no': company.phone_no,
                        'company_logo': company.company_logo.url if company.company_logo else None,
                    }
            except Exception:
                return {}
        elif obj.seller_location == 'offsite':
            return {
                'address': obj.address,
                'country': obj.country.name if obj.country else None,
                'state': obj.state.name if obj.state else None,
                'city': obj.city,
                'zipcode': obj.zipcode,
            }
        return {}

    def get_inventory_items(self, obj):
        """Get filtered inventory items based on query parameters"""
        request = self.context.get('request')
        inventory = obj.inventory_set.filter(deleted_at__isnull=True)
        
        if request:
            inventory = self._apply_filters(inventory, request)
        
        return InventorySerializer(inventory, many=True, context=self.context).data

    def get_lot_count(self, obj):
        """Get filtered lot count"""
        request = self.context.get('request')
        inventory = obj.inventory_set.filter(deleted_at__isnull=True)
        
        if request:
            inventory = self._apply_filters(inventory, request)
        
        return inventory.count()

    def get_categories(self, obj):
        """Get all categories used in this auction's lots"""
        categories = Category.objects.filter(
            inventory__auction=obj,
            inventory__deleted_at__isnull=True,
            deleted_at__isnull=True
        ).distinct()
        return CategorySerializer(categories, many=True).data

    def get_bid_range(self, obj):
        """Get min and max bid amounts for this auction"""
        inventory_items = obj.inventory_set.filter(deleted_at__isnull=True)
        bid_amounts = []
        
        for item in inventory_items:
            current_bid = self._get_current_bid_amount(item)
            bid_amounts.append(current_bid)
        
        if bid_amounts:
            return {
                'min': min(bid_amounts),
                'max': max(bid_amounts)
            }
        return {'min': 0, 'max': 0}

    def _apply_filters(self, inventory, request):
        """Apply all filters to inventory queryset"""
        search = request.GET.get('search', '').strip()
        categories = request.GET.getlist('categories')
        min_bid = request.GET.get('min_bid')
        max_bid = request.GET.get('max_bid')
        status = request.GET.get('status')
        sort_by = request.GET.get('sort_by', 'closing_soon')
        
        # Search filter
        if search:
            inventory = inventory.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(inventory_number__icontains=search)
            )
        
        # Category filter
        if categories:
            inventory = inventory.filter(category_id__in=categories)
        
        # Bid range filter
        if min_bid or max_bid:
            filtered_ids = []
            for item in inventory:
                current_bid = self._get_current_bid_amount(item)
                include_item = True
                if min_bid and current_bid < float(min_bid):
                    include_item = False
                if max_bid and current_bid > float(max_bid):
                    include_item = False
                if include_item:
                    filtered_ids.append(item.id)
            inventory = inventory.filter(id__in=filtered_ids)
        
        # Status filter
        if status:
            now = timezone.now()
            if status == 'open':
                inventory = inventory.filter(lot_end_time__gt=now)
            elif status == 'closed':
                inventory = inventory.filter(lot_end_time__lte=now)
        
        # Sorting
        if sort_by == 'closing_soon':
            inventory = inventory.order_by('lot_end_time')
        elif sort_by in ['lowest_bid', 'highest_bid']:
            # Will be handled in view
            pass
        elif sort_by == 'title_asc':
            inventory = inventory.order_by('title')
        elif sort_by == 'title_desc':
            inventory = inventory.order_by('-title')
        
        return inventory

    def _get_current_bid_amount(self, inventory_item):
        """Helper method to get current bid amount for an inventory item"""
        highest_bid = inventory_item.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return float(highest_bid.bid_amount) if highest_bid else float(inventory_item.starting_bid)
################################################################################################################
class CategoryLotsSerializer(serializers.Serializer):
    """Serializer for category-based lot listing with pagination"""
    category_info = serializers.SerializerMethodField()
    inventory_items = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    bid_range = serializers.SerializerMethodField()
    pagination = serializers.SerializerMethodField()

    def get_category_info(self, obj):
        """Get category information"""
        category_ids = self._get_category_ids()
        if category_ids:  # Only if categories are specified
            try:
                # If single category, return its info
                if len(category_ids) == 1:
                    category = Category.objects.get(id=category_ids[0])
                    return CategorySerializer(category).data
                else:
                    # If multiple categories, return list of category info
                    categories = Category.objects.filter(id__in=category_ids)
                    return CategorySerializer(categories, many=True).data
            except Category.DoesNotExist:
                pass
        return None

    def get_inventory_items(self, obj):
        """Get filtered inventory items for categories with pagination"""
        request = self.context.get('request')
        category_ids = self._get_category_ids()
        current_time = timezone.now()
        
        # Get base queryset - if no categories, get all lots
        if category_ids:
            inventory = Inventory.objects.filter(
                category_id__in=category_ids,
                deleted_at__isnull=True,
                lot_end_time__isnull=False,  # Only lots with end time
                lot_end_time__gt=current_time  # Only active lots (not expired)
            )
        else:
            # If no categories specified, get all lots
            inventory = Inventory.objects.filter(
                deleted_at__isnull=True,
                lot_end_time__isnull=False,  # Only lots with end time
                lot_end_time__gt=current_time  # Only active lots (not expired)
            )
        
        inventory = inventory.select_related('auction', 'category').prefetch_related('media_items', 'bids')
        
        if request:
            inventory = self._apply_filters(inventory, request)
        
        # Apply pagination
        page = int(request.GET.get('page', 1)) if request else 1
        page_size = int(request.GET.get('page_size', 20)) if request else 20
        
        paginator = Paginator(inventory, page_size)
        page_obj = paginator.get_page(page)
        
        # Store pagination info for get_pagination method
        self._pagination_info = {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
        
        # Serialize the paginated inventory items
        from .serializers import InventorySerializer  # Import your inventory serializer
        return InventorySerializer(page_obj.object_list, many=True, context=self.context).data

    def get_categories(self, obj):
        """Get only subcategories for filtering (exclude parent categories)"""
        # Filter to get only subcategories (categories that have a parent)
        subcategories = Category.objects.filter(
            deleted_at__isnull=True,
            parent__isnull=False  # Only subcategories (have parent)
        ).distinct()
        
        # Use a custom serializer or modify the data to exclude subcategories field
        categories_data = []
        for category in subcategories:
            category_data = {
                'id': category.id,
                'name': category.name,
                # Exclude subcategories field entirely
            }
            # Add any other fields you need from CategorySerializer except subcategories
            categories_data.append(category_data)
        
        return categories_data

    def get_bid_range(self, obj):
        """Get min and max bid amounts for category lots"""
        category_ids = self._get_category_ids()
        current_time = timezone.now()
        
        # If no categories specified, get all lots
        if category_ids:
            inventory_items = Inventory.objects.filter(
                category_id__in=category_ids,
                deleted_at__isnull=True,
                lot_end_time__isnull=False,
                lot_end_time__gt=current_time
            )
        else:
            inventory_items = Inventory.objects.filter(
                deleted_at__isnull=True,
                lot_end_time__isnull=False,
                lot_end_time__gt=current_time
            )
        
        bid_amounts = []
        for item in inventory_items:
            current_bid = self._get_current_bid_amount(item)
            bid_amounts.append(current_bid)
        
        if bid_amounts:
            return {
                'min': min(bid_amounts),
                'max': max(bid_amounts)
            }
        return {'min': 0, 'max': 0}

    def get_pagination(self, obj):
        """Get pagination information"""
        return getattr(self, '_pagination_info', {})

    def _get_category_ids(self):
        """Helper method to get category IDs from request"""
        request = self.context.get('request')
        if not request:
            return []
        
        # Check for comma-separated category_id parameter
        category_id_param = request.GET.get('category_id', '').strip()
        if category_id_param:
            try:
                # Split by comma and convert to integers, filter out empty strings
                category_ids = [int(id.strip()) for id in category_id_param.split(',') if id.strip()]
                return category_ids
            except (ValueError, TypeError):
                pass
        
        # Fallback to individual category parameters (if any)
        categories = request.GET.getlist('categories')
        if categories:
            try:
                return [int(cat) for cat in categories if cat]
            except (ValueError, TypeError):
                pass
        
        # Return empty list if no valid categories found
        return []

    def _apply_filters(self, inventory, request):
        """Apply all filters to inventory queryset"""
        search = request.GET.get('search', '').strip()
        min_bid = request.GET.get('min_bid')
        max_bid = request.GET.get('max_bid')
        status = request.GET.get('status')
        sort_by = request.GET.get('sort_by', 'closing_soon')
        
        # Search filter
        if search:
            inventory = inventory.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(inventory_number__icontains=search)
            )
        
        # Bid range filter - Fallback to original approach for compatibility
        if min_bid or max_bid:
            filtered_ids = []
            for item in inventory:
                current_bid = self._get_current_bid_amount(item)
                include_item = True
                
                if min_bid:
                    try:
                        if current_bid < float(min_bid):
                            include_item = False
                    except (ValueError, TypeError):
                        pass
                
                if max_bid:
                    try:
                        if current_bid > float(max_bid):
                            include_item = False
                    except (ValueError, TypeError):
                        pass
                
                if include_item:
                    filtered_ids.append(item.id)
            
            inventory = inventory.filter(id__in=filtered_ids)
        
        # Status filter
        if status:
            now = timezone.now()
            if status == 'open':
                inventory = inventory.filter(lot_end_time__gt=now)
            elif status == 'closed':
                inventory = inventory.filter(lot_end_time__lte=now)
        
        # Sorting
        if sort_by == 'closing_soon':
            inventory = inventory.order_by('lot_end_time')
        elif sort_by == 'title_asc':
            inventory = inventory.order_by('title')
        elif sort_by == 'title_desc':
            inventory = inventory.order_by('-title')
        elif sort_by == 'lowest_bid':
            inventory = inventory.order_by('starting_bid')
        elif sort_by == 'highest_bid':
            inventory = inventory.order_by('-starting_bid')
        
        return inventory

    def _get_current_bid_amount(self, inventory_item):
        """Helper method to get current bid amount for an inventory item"""
        highest_bid = inventory_item.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return float(highest_bid.bid_amount) if highest_bid else float(inventory_item.starting_bid)    
################################################################################################################
class InventoryDetailSerializer(serializers.ModelSerializer):
    media_items = MediaSerializer(many=True, read_only=True)
    current_bid = serializers.SerializerMethodField()
    next_required_bid = serializers.SerializerMethodField()
    high_bidder = serializers.SerializerMethodField()
    reserve_met = serializers.SerializerMethodField()
    bid_history = serializers.SerializerMethodField()
    winner_data = serializers.SerializerMethodField()  # ✅ Add this line
    # winning_amount = serializers.SerializerMethodField()  # ✅ Add this line
    category = CategorySerializer(read_only=True)  # Add this line
    remaining_lots = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [
            'id', 'title', 'status', 'description', 'starting_bid', 'reserve_price', 'lot_start_time', 'lot_end_time',
            'media_items', 'current_bid', 'next_required_bid', 'high_bidder', 'reserve_met', 'bid_history', 'winner_data', 'category', 'remaining_lots'
        ]

    def get_current_bid(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True, auction=obj.auction).order_by('-bid_amount').first()
        return latest_bid.bid_amount if latest_bid else obj.starting_bid

    def get_next_required_bid(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True, auction=obj.auction).order_by('-bid_amount').first()
        current = latest_bid.bid_amount if latest_bid else obj.starting_bid
        return current + obj.auction.bid_increment

    def get_high_bidder(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True, auction=obj.auction).order_by('-bid_amount').first()
        return latest_bid.user.username if latest_bid else None

    def get_reserve_met(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True, auction=obj.auction).order_by('-bid_amount').first()
        return (latest_bid.bid_amount >= obj.reserve_price) if latest_bid else False

    def get_bid_history(self, obj):
        bids = obj.bids.filter(
            deleted_at__isnull=True,
            auction=obj.auction
            ).order_by('-created_at')
        return [
            {
                "bidder": bid.user.username,
                "profile": bid.user.profile.photo.url if bid.user.profile.photo else None,
                "amount": bid.bid_amount,
                "auction_id": bid.auction.id,
                "timestamp": bid.created_at
            } for bid in bids
        ]
    
    def get_winner_data(self, obj):
        winning_bid = obj.winning_bid
        if winning_bid and winning_bid.user:
            user = winning_bid.user
            profile_photo = user.profile.photo.url if hasattr(user, 'profile') and user.profile.photo else None
            return {
                'user_id': user.id,
                'username': user.username,
                'profile_photo': profile_photo,
                'winning_amount': str(winning_bid.bid_amount),
                'status': 'sold'
            }
        return None

    def get_remaining_lots(self, obj):
        # Get all lots in the same auction that come after the current lot
        remaining_lots = Inventory.objects.filter(
            auction=obj.auction,
            deleted_at__isnull=True,
            id__gt=obj.id  # Only lots with ID greater than current lot
        ).order_by('id')  # Or 'lot_number' if you have that field
        
        return [
            {
                'id': lot.id,
                'title': lot.title,
                'thumbnail': lot.media_items.first().path if lot.media_items.exists() else None,
                'current_bid': self.get_current_bid(lot),  # Reuse your existing method
                'lot_end_time': lot.lot_end_time
            }
            for lot in remaining_lots
        ]
################################################################################################################
class PaymentChargeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentChargeDetail
        fields = ['charge_type', 'description', 'per_day_amount', 'days', 'total_amount']
################################################################################################################
class PaymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for user's payment history"""

    # Lot/Inventory details
    lot_name = serializers.CharField(source='inventory.title', read_only=True)
    lot_image = serializers.SerializerMethodField()
    lot_id = serializers.IntegerField(source='inventory.id', read_only=True)
    inventory_number = serializers.CharField(source='inventory.inventory_number', read_only=True)
    lot_condition = serializers.CharField(source='inventory.condition', read_only=True)
    
    
    # Auction details
    auction_name = serializers.CharField(source='inventory.auction.name', read_only=True)
    auction_id = serializers.IntegerField(source='inventory.auction.id', read_only=True)
    
    # Payment details
    price = serializers.CharField(source='amount', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    date = serializers.DateTimeField(source='created_at', read_only=True)
    updated_date = serializers.DateTimeField(source='updated_at', read_only=True)
    
    # For filtering
    payment_status_filter = serializers.SerializerMethodField()


    charges = PaymentChargeDetailSerializer(source='charge_details', many=True, read_only=True)
    buyers_premium = serializers.SerializerMethodField()
    total_charges = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()


    class Meta:
        model = Payment_History
        fields = [
            'id', 'transaction_id', 'lot_name', 'lot_image', 'lot_id', 
            'inventory_number', 'lot_condition', 'auction_name', 'auction_id',
            'price', 'status', 'status_display', 'payment_method', 
            'payment_method_display', 'date', 'updated_date', 'payment_status_filter', 'charges', 'buyers_premium',
            'total_charges', 'grand_total'
        ]

    def get_lot_image(self, obj):
        """Get the first image of the lot"""
        if obj.inventory:
            first_media = obj.inventory.media_items.filter(deleted_at__isnull=True).first()
            if first_media:
                if hasattr(first_media, 'media_file') and first_media.media_file:
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(first_media.media_file.url)
                elif hasattr(first_media, 'path') and first_media.path:
                    return first_media.path
        return None

    def get_payment_status_filter(self, obj):
        """Get status for filtering tabs"""
        if obj.status == Payment_History.PaymentStatus.PENDING:
            return 'pending'
        elif obj.status == Payment_History.PaymentStatus.COMPLETED:
            return 'paid'
        elif obj.status in [Payment_History.PaymentStatus.FAILED, Payment_History.PaymentStatus.REFUNDED]:
            return 'failed'
        return 'unknown'
    
    def get_buyers_premium(self, obj):
        if obj.inventory.auction and obj.inventory.auction.buyers_premium:
            return (obj.amount * obj.inventory.auction.buyers_premium) / 100
        return 0

    def get_total_charges(self, obj):
        return sum([charge.total_amount for charge in obj.charge_details.all()])

    def get_grand_total(self, obj):
        return obj.amount + self.get_buyers_premium(obj) + self.get_total_charges(obj)
################################################################################################################
class CompanyListingSerializer(serializers.ModelSerializer):
    """Serializer for company listing with state and country names"""
    country_name = serializers.CharField(source='country.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    company_logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'address', 'phone_no', 'city', 'zipcode',
            'country', 'country_name', 'state', 'state_name', 
            'company_logo', 'company_logo_url', 'latitude', 'longitude'
        ]
    
    def get_company_logo_url(self, obj):
        """Get full URL for company logo"""
        if obj.company_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.company_logo.url)
            return obj.company_logo.url
        return None
################################################################################################################
class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__' 
################################################################################################################
class WatchlistSerializer(serializers.ModelSerializer):
    inventory_details = serializers.SerializerMethodField()
    current_bid = serializers.SerializerMethodField()
    
    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'inventory', 'inventory_details', 'created_at', 'current_bid']
        read_only_fields = ['user', 'created_at']
    
    def get_inventory_details(self, obj):
        inventory = obj.inventory
        return {
            'id': inventory.id,
            'title': inventory.title,
            'image_url': inventory.media_items.first().path if inventory.media_items.exists() else None,           
            'starting_bid': inventory.starting_bid,
            'lot_end_time': inventory.lot_end_time,
        }   

    def get_current_bid(self, obj):
        """Returns either highest bid or starting bid"""
        highest_bid = obj.inventory.bids.filter(deleted_at__isnull=True) \
                                      .order_by('-bid_amount') \
                                      .first()
        return float(highest_bid.bid_amount) if highest_bid else float(obj.inventory.starting_bid)    
################################################################################################################
class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'username', 'profile_photo', 'user']
        read_only_fields = ['id', 'created_at', 'username', 'profile_photo']

    def get_profile_photo(self, obj):
        photo = getattr(obj.user.profile, 'photo', None)

        if photo and hasattr(photo, 'url'):
            return f"/media/{photo.name}"  # Ensures /media/ prefix
        else:
            return "/media/defaults/user-default.png"  # Fallback default       
          
################################################################################################################
class ActiveLotSerializer(serializers.ModelSerializer):
    auction_details = serializers.SerializerMethodField()
    category_details = serializers.SerializerMethodField()
    current_bid = serializers.SerializerMethodField()
    next_required_bid = serializers.SerializerMethodField()
    bid_increment = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    media_items = serializers.SerializerMethodField() 
    class Meta:
        model = Inventory
        fields = [
            'id', 'title', 'description', 'starting_bid', 'reserve_price',
            'lot_start_time', 'lot_end_time', 'status', 'condition', 'media_items',
            'auction_details', 'category_details', 'current_bid',
            'next_required_bid', 'bid_increment', 'time_remaining'
        ]
        
    def get_media_items(self, obj):
        # Get just the first media item
        first_media = obj.media_items.first()
        if first_media:
            return MediaSerializer(first_media).data
        return None

    def get_auction_details(self, obj):
        return {
            'id': obj.auction.id,
            'name': obj.auction.name,
            'start_date': obj.auction.start_date,
            'end_date': obj.auction.end_date,
            'is_featured': obj.auction.is_featured
        }

    def get_category_details(self, obj):
        if obj.category.parent:
            return {
                'category_id': obj.category.id,
                'category_name': obj.category.name,
                'subcategory_id': obj.category.parent.id,
                'subcategory_name': obj.category.parent.name
            }
        return {
            'category_id': obj.category.id,
            'category_name': obj.category.name
        }

    def get_current_bid(self, obj):
        highest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return str(highest_bid.bid_amount) if highest_bid else str(obj.starting_bid)

    def get_next_required_bid(self, obj):
        highest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        current = float(highest_bid.bid_amount) if highest_bid else float(obj.starting_bid)
        increment = float(obj.auction.bid_increment) if obj.auction.bid_increment else 100.00
        return str(current + increment)

    def get_bid_increment(self, obj):
        return str(obj.auction.bid_increment) if obj.auction.bid_increment else "100.00"

    def get_time_remaining(self, obj):
        if obj.lot_end_time:
            remaining = obj.lot_end_time - timezone.now()
            return str(remaining) if remaining.total_seconds() > 0 else "00:00:00"
        return None  
################################################################################################################
# SELLER DASHBORD #
################################################################################################################
class InventorySerializerForSeller(serializers.ModelSerializer):
    buyer = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name')
    
    class Meta:
        model = Inventory
        fields = ['id', 'title', 'category', 'starting_bid', 'status', 'buyer']
    
    def get_buyer(self, obj):
        if obj.winning_user:
            return obj.winning_user.username
        return None
    
class BidHistorySerializerForSeller(serializers.ModelSerializer):
    bidder = serializers.CharField(source='user.username')
    bid_amount = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='created_at', format='%Y-%m-%d')
    
    class Meta:
        model = Bid
        fields = ['bidder', 'bid_amount', 'date']
    
    def get_bid_amount(self, obj):  # Changed from get_amount to get_bid_amount
        return f"${obj.amount:.2f}"  # Assuming the field in Bid model is 'amount'