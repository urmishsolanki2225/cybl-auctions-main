import json
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from adminpanel.models import Inventory, Bid, Auctions, Comment
from decimal import Decimal
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class LotBiddingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            print(f"WebSocket connection attempt for lot: {self.scope['url_route']['kwargs']}")
            
            self.lot_id = self.scope['url_route']['kwargs']['lot_id']
            self.room_group_name = f'lot_{self.lot_id}'
            
            print(f"Lot ID: {self.lot_id}, Room: {self.room_group_name}")
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            print("Added to channel group")

            auction = await database_sync_to_async(lambda: Inventory.objects.get(id=self.lot_id).auction)()
            self.auction_group_name = f'auction_{auction.id}'
            await self.channel_layer.group_add(
                self.auction_group_name,
                self.channel_name
            )

            await self.accept()
            print("WebSocket connection accepted")
            
            # Send current lot status when user connects
            lot_data = await self.get_lot_data()
            print(f"Lot data: {lot_data}")
            
            await self.send(text_data=json.dumps({
                'type': 'lot_status',
                'data': lot_data
            }))
            print("Sent lot status")
            
        except Exception as e:
            print(f"Error in connect: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Connection error: {str(e)}'
            }))

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Leave auction group
        if hasattr(self, 'auction_group_name'):
            await self.channel_layer.group_discard(
                self.auction_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            print(f"Received data: {text_data}")
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'place_bid':
                user_id = text_data_json.get('user_id')
                bid_amount = Decimal(str(text_data_json.get('bid_amount', 0)))
                await self.place_bid(bid_amount, user_id)
            elif message_type == 'post_comment':
                user_id = text_data_json.get('user_id')
                comment_text = text_data_json.get('comment_text')
                await self.post_comment(comment_text, user_id)
            elif message_type == 'get_status':
                lot_data = await self.get_lot_data()
                await self.send(text_data=json.dumps({
                    'type': 'lot_status',
                    'data': lot_data
                }))
        except Exception as e:
            print(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Receive error: {str(e)}'
            }))
        
    async def post_comment(self, comment_text, user_id=None):
        """Handle posting a new comment via WebSocket"""
        try:
            print(f"Posting comment: {comment_text} for user: {user_id}")
            
            if not user_id:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'User ID is required to post a comment'
                }))
                return
                
            if not comment_text or not comment_text.strip():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Comment text cannot be empty'
                }))
                return
            
            try:
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                print(f"Found user: {user.username}")
            except User.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid user ID'
                }))
                return
            
            lot = await database_sync_to_async(Inventory.objects.get)(id=self.lot_id)
            auction = await database_sync_to_async(lambda: lot.auction)()
            
            # Create the comment
            comment = await database_sync_to_async(Comment.objects.create)(
                auction=auction,
                inventory=lot,
                user=user,
                content=comment_text.strip()
            )
            
            # Get user profile photo safely
            profile_photo = None
            try:
                profile_photo = await database_sync_to_async(
                    lambda: user.profile.photo.url if hasattr(user, 'profile') and user.profile.photo else None
                )()
            except:
                profile_photo = None
            
            # Prepare comment data for broadcasting
            comment_data = {
                'id': comment.id,
                'content': comment.content,
                'username': user.username,
                'user_id': user.id,
                'profile_photo': profile_photo,
                'created_at': comment.created_at.isoformat(),
            }
            
            # Broadcast the new comment to all users in the lot room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'comment_posted',
                    'comment_data': comment_data
                }
            )
            
            print(f"✅ Comment broadcast for lot {self.lot_id}")
            
        except Exception as e:
            print(f"Error in post_comment: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to post comment: {str(e)}'
            }))

    async def place_bid(self, bid_amount, user_id=None):
        try:
            print(f"Placing bid: {bid_amount} for user: {user_id}")
            
            if not user_id:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'User ID is required to place a bid'
                }))
                return
            
            try:
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                print(f"Found user: {user.username}")
            except User.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid user ID'
                }))
                return
            
            lot = await database_sync_to_async(Inventory.objects.get)(id=self.lot_id)
            auction = await database_sync_to_async(lambda: lot.auction)()
            print(f"Found lot: {lot.title}")
            
            now = timezone.now()
            
            # Check if we need to extend the timer BEFORE checking if bidding ended
            should_extend, extension_amount = await self.check_and_extend_timer(lot, now)
            
            # If timer was extended, update the lot and all subsequent lots
            if should_extend:
                await database_sync_to_async(self.update_lot_end_time)(lot, extension_amount)
                # Refresh lot object after extension
                lot = await database_sync_to_async(Inventory.objects.get)(id=self.lot_id)
                print(f"✅ Lot refreshed after extension. New end time: {lot.lot_end_time}")
            
            # Now check if bidding has ended (using updated end time)
            if lot.lot_end_time and lot.lot_end_time < now:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Bidding has ended for this lot'
                }))
                return
            
            # Determine bid type based on timing
            bid_type = 'Pre Bid'  # Default to pre-bid
            
            if lot.lot_start_time and lot.lot_start_time <= now:
                bid_type = 'Live Bid'
            elif lot.lot_start_time and lot.lot_start_time > now:
                bid_type = 'Pre Bid'
            
            print(f"Bid type determined: {bid_type}")
            
            # Get current highest bid
            current_bid = await self.get_current_bid(lot)
            required_bid = current_bid + auction.bid_increment if current_bid else lot.starting_bid
            
            if bid_amount < required_bid:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Bid must be at least ₹{required_bid}'
                }))
                return
            
            # Create bid with appropriate type
            bid = await database_sync_to_async(Bid.objects.create)(
                user=user,
                auction=auction,
                inventory=lot,
                bid_amount=bid_amount,
                type=bid_type
            )
            print(f"Created bid: {bid.id} of type: {bid_type}")
            
            # Check if reserve is met
            reserve_met = bid_amount >= lot.reserve_price

            # Get updated bid history after the new bid
            bid_history = await self.get_bid_history(lot)
            
            # Prepare bid data with updated lot end time
            bid_data = {
                'bidder': user.username,
                'user_id': user.id,
                'amount': str(bid_amount),
                'timestamp': bid.created_at.isoformat(),
                'reserve_met': reserve_met,
                'next_required_bid': str(bid_amount + auction.bid_increment),
                'bid_type': bid_type,
                'lot_end_time': lot.lot_end_time.isoformat() if lot.lot_end_time else None,
                'timer_extended': should_extend,
                'bid_history': bid_history
            }
            
            # Broadcast to all users in the lot room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bid_placed',
                    'bid_data': bid_data
                }
            )
            
            # Send timer extension notification if applicable
            if should_extend:
                # Broadcast to current lot
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'timer_extended',
                        'data': {
                            'lot_id': self.lot_id,
                            'new_end_time': lot.lot_end_time.isoformat(),
                            'extended_by_seconds': extension_amount,
                            'message': f'Timer extended by {extension_amount} seconds due to last-minute bid!'
                        }
                    }
                )
                
                # Broadcast schedule update to all lots in auction
                await self.channel_layer.group_send(
                    f'auction_{auction.id}',
                    {
                        'type': 'schedule_updated',
                        'data': {
                            'auction_id': auction.id,
                            'extended_by_seconds': extension_amount,
                            'trigger_lot_id': self.lot_id,
                            'message': f'Auction schedule updated due to lot {self.lot_id} extension'
                        }
                    }
                )
            
            # Send reserve met notification if applicable
            if reserve_met and current_bid < lot.reserve_price:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'reserve_met',
                        'data': {
                            'lot_id': self.lot_id,
                            'reserve_price': str(lot.reserve_price)
                        }
                    }
                )
                
        except Exception as e:
            print(f"Error in place_bid: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def check_and_extend_timer(self, lot, current_time):
        """
        FIXED: Standard auto-extend logic with proper return values
        """
        try:
            if not lot.lot_end_time:
                return False, 0

            # Fetch related auction with auto extend settings
            auction = await database_sync_to_async(lambda: lot.auction)()
            
            # Check if auto-extend is enabled
            if not auction.auto_extend_time or not auction.auto_extend_duration:
                print(f"Auto-extend disabled for auction {auction.id}")
                return False, 0

            # Calculate time remaining until lot ends
            time_remaining = lot.lot_end_time - current_time
            
            # Convert to seconds for easier comparison
            time_remaining_seconds = time_remaining.total_seconds()
            extension_threshold_seconds = 10  # 10 seconds threshold
            extension_amount_seconds = auction.auto_extend_duration

            print(f"🕐 Time remaining: {time_remaining_seconds} seconds")
            print(f"🕐 Extension threshold: {extension_threshold_seconds} seconds")
            print(f"🕐 Extension amount: {extension_amount_seconds} seconds")

            # If bid placed within the last 10 seconds, extend
            if 0 < time_remaining_seconds <= extension_threshold_seconds:
                print(f"✅ Timer extension triggered for lot {lot.id}")
                return True, extension_amount_seconds
            else:
                print(f"❌ No timer extension needed. Time remaining: {time_remaining_seconds}s")
                return False, 0

        except Exception as e:
            print(f"❌ Error in check_and_extend_timer: {str(e)}")
            return False, 0

    def update_lot_end_time(self, lot, extension_seconds):
        """
        FIXED: Update lot end time and properly cascade to subsequent lots
        """
        from django.db import transaction
        
        try:        
            with transaction.atomic():
                # Get original end time before any changes
                original_end_time = lot.lot_end_time
                print(f"🔄 Original end time: {original_end_time}")
                
                # Calculate new end time
                extension_amount = timedelta(seconds=extension_seconds)
                new_end_time = original_end_time + extension_amount
                
                print(f"🔄 Extending lot {lot.id} by {extension_seconds} seconds")
                print(f"🔄 New end time: {new_end_time}")
                
                # Update current lot
                lot.lot_end_time = new_end_time
                lot.save(update_fields=['lot_end_time'])
                
                # Verify the save worked
                lot.refresh_from_db()
                print(f"✅ Lot {lot.id} end time updated to: {lot.lot_end_time}")
                
                # Get auction
                auction = lot.auction
                
                # CRITICAL FIX: Find all subsequent lots that START after the ORIGINAL end time
                # This ensures we don't miss any lots that should be rescheduled
                subsequent_lots = Inventory.objects.filter(
                    auction=auction,
                    lot_start_time__gte=original_end_time,  # Changed from __gt to __gte
                    deleted_at__isnull=True
                ).exclude(id=lot.id).order_by('lot_start_time')
                
                print(f"🔄 Found {subsequent_lots.count()} subsequent lots to reschedule")
                
                # Update subsequent lots' start and end times
                for subsequent_lot in subsequent_lots:
                    old_start = subsequent_lot.lot_start_time
                    old_end = subsequent_lot.lot_end_time
                    
                    # Extend start time
                    subsequent_lot.lot_start_time += extension_amount
                    # Extend end time
                    if subsequent_lot.lot_end_time:
                        subsequent_lot.lot_end_time += extension_amount
                    
                    subsequent_lot.save(update_fields=['lot_start_time', 'lot_end_time'])
                    
                    print(f"✅ Lot {subsequent_lot.id} rescheduled:")
                    print(f"   Start: {old_start} -> {subsequent_lot.lot_start_time}")
                    print(f"   End: {old_end} -> {subsequent_lot.lot_end_time}")
                
                # Update auction end date if necessary
                if auction.end_date:
                    # Check if auction end date needs to be extended
                    last_lot = Inventory.objects.filter(
                        auction=auction,
                        deleted_at__isnull=True
                    ).order_by('-lot_end_time').first()
                    
                    if last_lot and last_lot.lot_end_time:
                        # Extend auction end date to match the last lot's end time
                        if auction.end_date < last_lot.lot_end_time:
                            old_auction_end = auction.end_date
                            auction.end_date = last_lot.lot_end_time
                            auction.save(update_fields=['end_date'])
                            print(f"✅ Auction {auction.id} end time extended:")
                            print(f"   {old_auction_end} -> {auction.end_date}")
                
                print(f"✅ Successfully extended lot {lot.id} and rescheduled subsequent lots")
                
        except Exception as e:
            print(f"❌ Error in update_lot_end_time: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    # Add the missing broadcast_lot_ended method
    async def broadcast_lot_ended(self, lot):
        """Broadcast lot ended with winner information"""
        try:
            # Get winner information
            winning_bid = await database_sync_to_async(
                lambda: lot.bids.filter(deleted_at__isnull=True)
                .order_by('-bid_amount', 'created_at').first()
            )()
            
            winner_data = None
            if winning_bid and winning_bid.bid_amount >= lot.reserve_price:
                # Get winner profile photo safely
                profile_photo = None
                try:
                    profile_photo = await database_sync_to_async(
                        lambda: winning_bid.user.profile.photo.url 
                        if hasattr(winning_bid.user, 'profile') and winning_bid.user.profile.photo 
                        else None
                    )()
                except Exception as e:
                    print(f"Error getting profile photo: {e}")
                
                winner_data = {
                    'user_id': winning_bid.user.id,
                    'username': winning_bid.user.username,
                    'profile_photo': profile_photo,
                    'winning_amount': str(winning_bid.bid_amount),
                    'status': 'sold'
                }
            else:
                winner_data = {
                    'status': 'unsold',
                    'reason': 'Reserve not met' if winning_bid else 'No bids received'
                }
            
            # Broadcast to all users in the lot room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'lot_ended',
                    'data': {
                        'lot_id': lot.id,
                        'lot_title': lot.title,
                        'winner': winner_data,
                        'ended_at': timezone.now().isoformat()
                    }
                }
            )
            
            # Also broadcast to auction group
            if hasattr(self, 'auction_group_name'):
                await self.channel_layer.group_send(
                    self.auction_group_name,
                    {
                        'type': 'lot_ended',
                        'data': {
                            'lot_id': lot.id,
                            'lot_title': lot.title,
                            'winner': winner_data,
                            'ended_at': timezone.now().isoformat()
                        }
                    }
                )
            
            print(f"✅ Broadcasted lot ended for lot {lot.id}")
            
        except Exception as e:
            print(f"❌ Error broadcasting lot ended: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @database_sync_to_async
    def get_user_profile_photo(user):
        try:
            return user.profile.photo.url if user.profile.photo else None
        except Exception as e:
            print(f"Error fetching profile photo: {e}")
            return None

    # WebSocket message handlers
    async def bid_placed(self, event):
        bid_data = event['bid_data']
        await self.send(text_data=json.dumps({
            'type': 'bid_placed',
            'data': bid_data
        }))

    async def comment_posted(self, event):
        """Handle comment_posted message type from group_send"""
        comment_data = event['comment_data']
        await self.send(text_data=json.dumps({
            'type': 'comment_posted',
            'data': comment_data
        }))

    async def timer_extended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'timer_extended',
            'data': event['data']
        }))

    async def reserve_met(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reserve_met',
            'data': event['data']
        }))
    
    async def schedule_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'schedule_updated',
            'data': event['data']
        }))

    async def lot_ended(self, event):
        """Handle lot ended event and send winner information"""
        await self.send(text_data=json.dumps({
            'type': 'lot_ended',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_bid_history(self, lot):
        """Get bid history for a lot"""
        try:
            bid_history = lot.bids.filter(deleted_at__isnull=True).order_by('-created_at')
            bid_history_data = []

            for bid in bid_history:
                bid_history_data.append({
                    'id': bid.id,
                    'bidder': bid.user.username,
                    'profile': getattr(bid.user.profile.photo, 'url', None),
                    'user_id': bid.user.id,
                    'amount': str(bid.bid_amount),
                    'timestamp': bid.created_at.isoformat(),
                    'type': bid.type
                })
            
            return bid_history_data
        except Exception as e:
            print(f"Error getting bid history: {str(e)}")
            return []
        
    @database_sync_to_async
    def get_current_bid(self, lot):
        try:
            latest_bid = lot.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
            return latest_bid.bid_amount if latest_bid else lot.starting_bid
        except Exception as e:
            print(f"Error getting current bid: {str(e)}")
            return lot.starting_bid

    @database_sync_to_async
    def get_lot_data(self):
        try:
            lot = Inventory.objects.get(id=self.lot_id)
            latest_bid = lot.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
            current_bid = latest_bid.bid_amount if latest_bid else lot.starting_bid

            # Get bid history - all bids for this lot ordered by time (newest first)
            bid_history = lot.bids.filter(deleted_at__isnull=True).order_by('-created_at')
            bid_history_data = []

            for bid in bid_history:
                bid_history_data.append({
                    'id': bid.id,
                    'bidder': bid.user.username,
                    'profile': getattr(bid.user.profile.photo, 'url', None),
                    'user_id': bid.user.id,
                    'amount': str(bid.bid_amount),
                    'timestamp': bid.created_at.isoformat(),
                    'type': bid.type
                })
            
            return {
                'lot_id': lot.id,
                'title': lot.title,
                'current_bid': str(current_bid),
                'next_required_bid': str(current_bid + lot.auction.bid_increment),
                'high_bidder': latest_bid.user.username if latest_bid else None,
                'reserve_met': current_bid >= lot.reserve_price,
                'reserve_price': str(lot.reserve_price),
                'lot_start_time': lot.lot_start_time.isoformat() if lot.lot_start_time else None,
                'lot_end_time': lot.lot_end_time.isoformat() if lot.lot_end_time else None,
                'bid_history': bid_history_data
            }
        except Inventory.DoesNotExist:
            print(f"Lot {self.lot_id} not found")
            return {
                'error': 'Lot not found',
                'lot_id': self.lot_id
            }
        except Exception as e:
            print(f"Error getting lot data: {str(e)}")
            return {
                'error': str(e),
                'lot_id': self.lot_id
            }