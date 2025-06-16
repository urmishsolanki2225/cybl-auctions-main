# # backend/api/consumers.py
# import json
# import traceback
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import User
# from adminpanel.models import Inventory, Bid, Auctions
# from decimal import Decimal
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class LotBiddingConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         try:
#             print(f"WebSocket connection attempt for lot: {self.scope['url_route']['kwargs']}")
            
#             self.lot_id = self.scope['url_route']['kwargs']['lot_id']
#             self.room_group_name = f'lot_{self.lot_id}'
            
#             print(f"Lot ID: {self.lot_id}, Room: {self.room_group_name}")
            
#             # Join room group
#             await self.channel_layer.group_add(
#                 self.room_group_name,
#                 self.channel_name
#             )
#             print("Added to channel group")

#             await self.accept()
#             print("WebSocket connection accepted")
            
#             # Send current lot status when user connects
#             lot_data = await self.get_lot_data()
#             print(f"Lot data: {lot_data}")
            
#             await self.send(text_data=json.dumps({
#                 'type': 'lot_status',
#                 'data': lot_data
#             }))
#             print("Sent lot status")
            
#         except Exception as e:
#             print(f"Error in connect: {str(e)}")
#             print(f"Traceback: {traceback.format_exc()}")
#             # Don't close here, let's see what the error is
#             await self.accept()
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': f'Connection error: {str(e)}'
#             }))

#     async def disconnect(self, close_code):
#         print(f"WebSocket disconnected with code: {close_code}")
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         try:
#             print(f"Received data: {text_data}")
#             text_data_json = json.loads(text_data)
#             message_type = text_data_json.get('type')
            
#             if message_type == 'place_bid':
#                 # Get user_id from the message payload
#                 user_id = text_data_json.get('user_id')
#                 bid_amount = Decimal(str(text_data_json.get('bid_amount', 0)))
#                 await self.place_bid(bid_amount, user_id)
#             elif message_type == 'get_status':
#                 lot_data = await self.get_lot_data()
#                 await self.send(text_data=json.dumps({
#                     'type': 'lot_status',
#                     'data': lot_data
#                 }))
#         except Exception as e:
#             print(f"Error in receive: {str(e)}")
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': f'Receive error: {str(e)}'
#             }))

#     # async def place_bid(self, bid_amount, user_id=None):
#     #     try:
#     #         print(f"Placing bid: {bid_amount} for user: {user_id}")
            
#     #         # Validate user_id is provided
#     #         if not user_id:
#     #             await self.send(text_data=json.dumps({
#     #                 'type': 'error',
#     #                 'message': 'User ID is required to place a bid'
#     #             }))
#     #             return
            
#     #         # Get user
#     #         try:
#     #             user = await database_sync_to_async(User.objects.get)(id=user_id)
#     #             print(f"Found user: {user.username}")
#     #         except User.DoesNotExist:
#     #             await self.send(text_data=json.dumps({
#     #                 'type': 'error',
#     #                 'message': 'Invalid user ID'
#     #             }))
#     #             return
            
#     #         # Get lot and validate bid
#     #         lot = await database_sync_to_async(Inventory.objects.get)(id=self.lot_id)
#     #         auction = await database_sync_to_async(lambda: lot.auction)()
#     #         print(f"Found lot: {lot.title}")
            
#     #         # Check if bidding is allowed (lot is active)
#     #         from django.utils import timezone
#     #         now = timezone.now()
#     #         if lot.lot_start_time and lot.lot_start_time > now:
#     #             await self.send(text_data=json.dumps({
#     #                 'type': 'error',
#     #                 'message': 'Bidding has not started for this lot'
#     #             }))
#     #             return
            
#     #         if lot.lot_end_time and lot.lot_end_time < now:
#     #             await self.send(text_data=json.dumps({
#     #                 'type': 'error',
#     #                 'message': 'Bidding has ended for this lot'
#     #             }))
#     #             return
            
#     #         # Get current highest bid
#     #         current_bid = await self.get_current_bid(lot)
#     #         required_bid = current_bid + auction.bid_increment if current_bid else lot.starting_bid
            
#     #         if bid_amount < required_bid:
#     #             await self.send(text_data=json.dumps({
#     #                 'type': 'error',
#     #                 'message': f'Bid must be at least ₹{required_bid}'
#     #             }))
#     #             return
            
#     #         # Create bid
#     #         bid = await database_sync_to_async(Bid.objects.create)(
#     #             user=user,
#     #             auction=auction,
#     #             inventory=lot,
#     #             bid_amount=bid_amount,
#     #             type='Pre Bid'
#     #         )
#     #         print(f"Created bid: {bid.id}")
            
#     #         # Check if reserve is met
#     #         reserve_met = bid_amount >= lot.reserve_price
            
#     #         # Broadcast to all users in the lot room
#     #         await self.channel_layer.group_send(
#     #             self.room_group_name,
#     #             {
#     #                 'type': 'bid_placed',
#     #                 'bid_data': {
#     #                     'bidder': user.username,
#     #                     'amount': str(bid_amount),
#     #                     'timestamp': bid.created_at.isoformat(),
#     #                     'reserve_met': reserve_met,
#     #                     'next_required_bid': str(bid_amount + auction.bid_increment)
#     #                 }
#     #             }
#     #         )
            
#     #         # Send reserve met notification if applicable
#     #         if reserve_met and current_bid < lot.reserve_price:
#     #             await self.channel_layer.group_send(
#     #                 self.room_group_name,
#     #                 {
#     #                     'type': 'reserve_met',
#     #                     'data': {
#     #                         'lot_id': self.lot_id,
#     #                         'reserve_price': str(lot.reserve_price)
#     #                     }
#     #                 }
#     #             )
                
#     #     except Exception as e:
#     #         print(f"Error in place_bid: {str(e)}")
#     #         print(f"Traceback: {traceback.format_exc()}")
#     #         await self.send(text_data=json.dumps({
#     #             'type': 'error',
#     #             'message': str(e)
#     #         }))
#     # Updated place_bid method in consumers.py

#     async def place_bid(self, bid_amount, user_id=None):
#         try:
#             print(f"Placing bid: {bid_amount} for user: {user_id}")
            
#             # Validate user_id is provided
#             if not user_id:
#                 await self.send(text_data=json.dumps({
#                     'type': 'error',
#                     'message': 'User ID is required to place a bid'
#                 }))
#                 return
            
#             # Get user
#             try:
#                 user = await database_sync_to_async(User.objects.get)(id=user_id)
#                 print(f"Found user: {user.username}")
#             except User.DoesNotExist:
#                 await self.send(text_data=json.dumps({
#                     'type': 'error',
#                     'message': 'Invalid user ID'
#                 }))
#                 return
            
#             # Get lot and validate bid
#             lot = await database_sync_to_async(Inventory.objects.get)(id=self.lot_id)
#             auction = await database_sync_to_async(lambda: lot.auction)()
#             print(f"Found lot: {lot.title}")
            
#             # Updated timing validation - Allow pre-bids
#             from django.utils import timezone
#             now = timezone.now()
            
#             # Only check if bidding has ended (applies to both live and pre-bids)
#             if lot.lot_end_time and lot.lot_end_time < now:
#                 await self.send(text_data=json.dumps({
#                     'type': 'error',
#                     'message': 'Bidding has ended for this lot'
#                 }))
#                 return
            
#             # Determine bid type based on timing
#             bid_type = 'Pre Bid'  # Default to pre-bid
            
#             if lot.lot_start_time and lot.lot_start_time <= now:
#                 # Lot has started, this is a live bid
#                 bid_type = 'Live Bid'
#             elif lot.lot_start_time and lot.lot_start_time > now:
#                 # Lot hasn't started yet, this is a pre-bid (allowed)
#                 bid_type = 'Pre Bid'
            
#             print(f"Bid type determined: {bid_type}")
            
#             # Get current highest bid
#             current_bid = await self.get_current_bid(lot)
#             required_bid = current_bid + auction.bid_increment if current_bid else lot.starting_bid
            
#             if bid_amount < required_bid:
#                 await self.send(text_data=json.dumps({
#                     'type': 'error',
#                     'message': f'Bid must be at least ₹{required_bid}'
#                 }))
#                 return
            
#             # Create bid with appropriate type
#             bid = await database_sync_to_async(Bid.objects.create)(
#                 user=user,
#                 auction=auction,
#                 inventory=lot,
#                 bid_amount=bid_amount,
#                 type=bid_type  # Use determined bid type
#             )
#             print(f"Created bid: {bid.id} of type: {bid_type}")
            
#             # Check if reserve is met
#             reserve_met = bid_amount >= lot.reserve_price
            
#             # Broadcast to all users in the lot room
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'bid_placed',
#                     'bid_data': {
#                         'bidder': user.username,
#                         'amount': str(bid_amount),
#                         'timestamp': bid.created_at.isoformat(),
#                         'reserve_met': reserve_met,
#                         'next_required_bid': str(bid_amount + auction.bid_increment),
#                         'bid_type': bid_type
#                     }
#                 }
#             )
            
#             # Send reserve met notification if applicable
#             if reserve_met and current_bid < lot.reserve_price:
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'reserve_met',
#                         'data': {
#                             'lot_id': self.lot_id,
#                             'reserve_price': str(lot.reserve_price)
#                         }
#                     }
#                 )
                
#         except Exception as e:
#             print(f"Error in place_bid: {str(e)}")
#             print(f"Traceback: {traceback.format_exc()}")
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': str(e)
#             }))

#     # Receive message from room group
#     async def bid_placed(self, event):
#         bid_data = event['bid_data']
        
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'type': 'bid_placed',
#             'data': bid_data
#         }))

#     async def reserve_met(self, event):
#         # Send reserve met notification
#         await self.send(text_data=json.dumps({
#             'type': 'reserve_met',
#             'data': event['data']
#         }))

#     @database_sync_to_async
#     def get_current_bid(self, lot):
#         try:
#             latest_bid = lot.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
#             return latest_bid.bid_amount if latest_bid else lot.starting_bid
#         except Exception as e:
#             print(f"Error getting current bid: {str(e)}")
#             return lot.starting_bid

#     @database_sync_to_async
#     def get_lot_data(self):
#         try:
#             lot = Inventory.objects.get(id=self.lot_id)
#             latest_bid = lot.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
#             current_bid = latest_bid.bid_amount if latest_bid else lot.starting_bid
            
#             return {
#                 'lot_id': lot.id,
#                 'title': lot.title,
#                 'current_bid': str(current_bid),
#                 'next_required_bid': str(current_bid + lot.auction.bid_increment),
#                 'high_bidder': latest_bid.user.username if latest_bid else None,
#                 'reserve_met': current_bid >= lot.reserve_price,
#                 'reserve_price': str(lot.reserve_price),
#                 'lot_start_time': lot.lot_start_time.isoformat() if lot.lot_start_time else None,
#                 'lot_end_time': lot.lot_end_time.isoformat() if lot.lot_end_time else None,
#             }
#         except Inventory.DoesNotExist:
#             print(f"Lot {self.lot_id} not found")
#             return {
#                 'error': 'Lot not found',
#                 'lot_id': self.lot_id
#             }
#         except Exception as e:
#             print(f"Error getting lot data: {str(e)}")
#             return {
#                 'error': str(e),
#                 'lot_id': self.lot_id
#             }
# backend/api/consumers.py
import json
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from adminpanel.models import Inventory, Bid, Auctions
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
            
            # Check if we need to extend the timer
            should_extend = await self.check_and_extend_timer(lot, now)
            
            # Only check if bidding has ended (applies to both live and pre-bids)
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
            
            # Refresh lot data to get updated end time if extended
            lot = await database_sync_to_async(Inventory.objects.get)(id=self.lot_id)
            
            # Check if reserve is met
            reserve_met = bid_amount >= lot.reserve_price
            
            # Prepare bid data with updated lot end time
            bid_data = {
                'bidder': user.username,
                'amount': str(bid_amount),
                'timestamp': bid.created_at.isoformat(),
                'reserve_met': reserve_met,
                'next_required_bid': str(bid_amount + auction.bid_increment),
                'bid_type': bid_type,
                'lot_end_time': lot.lot_end_time.isoformat() if lot.lot_end_time else None,
                'timer_extended': should_extend
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
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'timer_extended',
                        'data': {
                            'lot_id': self.lot_id,
                            'new_end_time': lot.lot_end_time.isoformat(),
                            'extended_by_minutes': 5,  # or whatever your extension is
                            'message': 'Timer extended by 5 minutes due to last-minute bid!'
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
        Check if timer should be extended and extend it if needed
        Returns True if timer was extended
        """
        try:
            if not lot.lot_end_time:
                return False
                
            # Check if bid is placed within last 5 minutes
            time_remaining = lot.lot_end_time - current_time
            extension_threshold = timedelta(minutes=5)
            
            if time_remaining <= extension_threshold and time_remaining > timedelta(0):
                # Extend timer by 5 minutes
                new_end_time = lot.lot_end_time + timedelta(minutes=5)
                
                await database_sync_to_async(self.update_lot_end_time)(lot, new_end_time)
                
                print(f"Timer extended for lot {lot.id} to {new_end_time}")
                return True
                
            return False
            
        except Exception as e:
            print(f"Error in check_and_extend_timer: {str(e)}")
            return False

    def update_lot_end_time(self, lot, new_end_time):
        """Update lot end time in database"""
        lot.lot_end_time = new_end_time
        lot.save(update_fields=['lot_end_time'])

    # WebSocket message handlers
    async def bid_placed(self, event):
        bid_data = event['bid_data']
        await self.send(text_data=json.dumps({
            'type': 'bid_placed',
            'data': bid_data
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