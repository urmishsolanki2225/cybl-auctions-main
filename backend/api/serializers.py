# backend\api\serializers.py
import re
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth.models import User
from adminpanel.models import Country, State, Media, Inventory, Profile, Auctions, Company, Category, Bid, Payment_History
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.db import models

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
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories', 'order']

    def get_subcategories(self, obj):
        children = obj.subcategories.filter(deleted_at__isnull=True).order_by('order')
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
    media_items = MediaSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    current_bid = serializers.SerializerMethodField()
    next_required_bid = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = '__all__' 

    def get_current_bid(self, obj):
        highest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return str(highest_bid.bid_amount) if highest_bid else str(obj.starting_bid)
    
    def get_next_required_bid(self, obj):
        highest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        current_bid = highest_bid.bid_amount if highest_bid else obj.starting_bid
        return str(current_bid + obj.auction.bid_increment)
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
    user = UserSerializer(read_only=True)  # ⬅️ Use custom serializer here
    location_details = serializers.SerializerMethodField()
    inventory_items = serializers.SerializerMethodField()
    lot_count = serializers.SerializerMethodField()  # 👈 New field
    

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
            # Apply filters based on query parameters
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
                for item in inventory:
                    current_bid = self._get_current_bid_amount(item)
                    if min_bid and current_bid < float(min_bid):
                        inventory = inventory.exclude(id=item.id)
                    if max_bid and current_bid > float(max_bid):
                        inventory = inventory.exclude(id=item.id)
            
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
            elif sort_by == 'lowest_bid':
                # Custom sorting by current bid amount (will be handled in view)
                pass
            elif sort_by == 'highest_bid':
                # Custom sorting by current bid amount (will be handled in view)
                pass
            elif sort_by == 'title_asc':
                inventory = inventory.order_by('title')
            elif sort_by == 'title_desc':
                inventory = inventory.order_by('-title')
        
        return InventorySerializer(inventory, many=True, context=self.context).data

    def get_lot_count(self, obj):
        """Get filtered lot count"""
        request = self.context.get('request')
        inventory = obj.inventory_set.filter(deleted_at__isnull=True)
        
        if request:
            search = request.GET.get('search', '').strip()
            categories = request.GET.getlist('categories')
            status = request.GET.get('status')
            
            if search:
                inventory = inventory.filter(
                    models.Q(title__icontains=search) |
                    models.Q(description__icontains=search) |
                    models.Q(inventory_number__icontains=search)
                )
            
            if categories:
                inventory = inventory.filter(category_id__in=categories)
            
            if status:
                now = timezone.now()
                if status == 'open':
                    inventory = inventory.filter(lot_end_time__gt=now)
                elif status == 'closed':
                    inventory = inventory.filter(lot_end_time__lte=now)
        
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

    def _get_current_bid_amount(self, inventory_item):
        """Helper method to get current bid amount for an inventory item"""
        highest_bid = inventory_item.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return float(highest_bid.bid_amount) if highest_bid else float(inventory_item.starting_bid)
################################################################################################################
# FOR AUCTIOSN DETAILS PAGE 
class InventoryBidInfoSerializer(serializers.ModelSerializer):
    current_bid = serializers.SerializerMethodField()
    next_required_bid = serializers.SerializerMethodField()
    high_bidder = serializers.SerializerMethodField()
    reserve_met = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)  # Add this line


    class Meta:
        model = Inventory
        fields = [
            'id', 'title', 'starting_bid', 'reserve_price', 'lot_start_time', 'lot_end_time',
            'current_bid', 'next_required_bid', 'high_bidder', 'reserve_met', 'category'
        ]

    def get_current_bid(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return latest_bid.bid_amount if latest_bid else obj.starting_bid

    def get_next_required_bid(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        current = latest_bid.bid_amount if latest_bid else obj.starting_bid
        return current + obj.auction.bid_increment

    def get_high_bidder(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return latest_bid.user.username if latest_bid else None

    def get_reserve_met(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return (latest_bid.bid_amount >= obj.reserve_price) if latest_bid else False    
################################################################################################################
# FOR ITEM DETAILS PAGE
class InventoryDetailSerializer(serializers.ModelSerializer):
    media_items = MediaSerializer(many=True, read_only=True)
    current_bid = serializers.SerializerMethodField()
    next_required_bid = serializers.SerializerMethodField()
    high_bidder = serializers.SerializerMethodField()
    reserve_met = serializers.SerializerMethodField()
    bid_history = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)  # Add this line

    class Meta:
        model = Inventory
        fields = [
            'id', 'title', 'description', 'starting_bid', 'reserve_price', 'lot_start_time', 'lot_end_time',
            'media_items', 'current_bid', 'next_required_bid', 'high_bidder', 'reserve_met', 'bid_history', 'category'
        ]

    def get_current_bid(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return latest_bid.bid_amount if latest_bid else obj.starting_bid

    def get_next_required_bid(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        current = latest_bid.bid_amount if latest_bid else obj.starting_bid
        return current + obj.auction.bid_increment

    def get_high_bidder(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return latest_bid.user.username if latest_bid else None

    def get_reserve_met(self, obj):
        latest_bid = obj.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return (latest_bid.bid_amount >= obj.reserve_price) if latest_bid else False

    def get_bid_history(self, obj):
        bids = obj.bids.filter(deleted_at__isnull=True).order_by('-created_at')
        return [
            {
                "bidder": bid.user.username,
                "amount": bid.bid_amount,
                "timestamp": bid.created_at
            } for bid in bids
        ]
################################################################################################################
class BiddingHistorySerializer(serializers.ModelSerializer):
    """Updated serializer for user's bidding history"""
    
    # Inventory details
    inventory_id = serializers.IntegerField(source='inventory.id', read_only=True)
    inventory_title = serializers.CharField(source='inventory.title', read_only=True)
    inventory_first_image = serializers.SerializerMethodField()
    
    # Auction details
    auction_name = serializers.CharField(source='inventory.auction.name', read_only=True)
    
    # Bid details
    highest_bid = serializers.SerializerMethodField()
    my_last_bid = serializers.SerializerMethodField()
    lot_end_time = serializers.DateTimeField(source='inventory.lot_end_time', read_only=True)
    
    # Status information
    bid_status = serializers.SerializerMethodField()
    is_winning = serializers.SerializerMethodField()
    reserve_met = serializers.SerializerMethodField()
    
    # Additional fields
    total_bids_by_me = serializers.SerializerMethodField()
    last_bid_time = serializers.SerializerMethodField()
    starting_bid = serializers.CharField(source='inventory.starting_bid', read_only=True)
    reserve_price = serializers.CharField(source='inventory.reserve_price', read_only=True)
    winning_user_id = serializers.IntegerField(source='inventory.winning_user.id', read_only=True)
    winning_bid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Bid
        fields = [
            'inventory_id', 'inventory_title', 'inventory_first_image', 'auction_name',
            'highest_bid', 'my_last_bid', 'lot_end_time', 'bid_status',
            'is_winning', 'reserve_met', 'total_bids_by_me', 'last_bid_time',
            'starting_bid', 'reserve_price', 'winning_user_id', 'winning_bid_amount'
        ]

    def get_inventory_first_image(self, obj):
        """Get the first image of the inventory item"""
        first_media = obj.inventory.media_items.filter(deleted_at__isnull=True).first()
        if first_media:
            if hasattr(first_media, 'media_file') and first_media.media_file:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(first_media.media_file.url)
            elif hasattr(first_media, 'path') and first_media.path:
                return first_media.path
        return None

    def get_highest_bid(self, obj):
        """Get the current highest bid for this inventory"""
        highest_bid = obj.inventory.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        return str(highest_bid.bid_amount) if highest_bid else str(obj.inventory.starting_bid)

    def get_my_last_bid(self, obj):
        """Get user's last bid for this inventory"""
        user = self.context.get('request').user
        last_bid = obj.inventory.bids.filter(
            user=user, deleted_at__isnull=True
        ).order_by('-created_at').first()
        return str(last_bid.bid_amount) if last_bid else None

    def get_bid_status(self, obj):
        """Determine the status of the bid (active, won, lost)"""
        now = timezone.now()
        inventory = obj.inventory
        user = self.context.get('request').user
        
        # Check if lot has ended
        if inventory.lot_end_time and inventory.lot_end_time <= now:
            # Lot has ended - check winning_user field
            if inventory.winning_user and inventory.winning_user == user:
                return 'won'
            else:
                return 'lost'
        else:
            # Lot is still active
            return 'active'

    def get_is_winning(self, obj):
        """Check if user is currently winning this lot"""
        user = self.context.get('request').user
        inventory = obj.inventory
        
        # If lot ended, check winning_user
        if inventory.lot_end_time and inventory.lot_end_time <= timezone.now():
            return inventory.winning_user == user
        else:
            # For active lots, check if user has highest bid
            highest_bid = inventory.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
            return highest_bid and highest_bid.user == user

    def get_reserve_met(self, obj):
        """Check if reserve price is met"""
        highest_bid = obj.inventory.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
        current_bid = highest_bid.bid_amount if highest_bid else obj.inventory.starting_bid
        return current_bid >= obj.inventory.reserve_price

    def get_total_bids_by_me(self, obj):
        """Get total number of bids by this user on this inventory"""
        user = self.context.get('request').user
        return obj.inventory.bids.filter(user=user, deleted_at__isnull=True).count()

    def get_last_bid_time(self, obj):
        """Get the time of user's last bid"""
        user = self.context.get('request').user
        last_bid = obj.inventory.bids.filter(
            user=user, deleted_at__isnull=True
        ).order_by('-created_at').first()
        return last_bid.created_at if last_bid else None

    def get_winning_bid_amount(self, obj):
        """Get the winning bid amount if available"""
        if obj.inventory.winning_bid:
            return str(obj.inventory.winning_bid.bid_amount)
        return None
################################################################################################################
# PAYMENT HISTORY
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

    class Meta:
        model = Payment_History
        fields = [
            'id', 'transaction_id', 'lot_name', 'lot_image', 'lot_id', 
            'inventory_number', 'lot_condition', 'auction_name', 'auction_id',
            'price', 'status', 'status_display', 'payment_method', 
            'payment_method_display', 'date', 'updated_date', 'payment_status_filter'
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