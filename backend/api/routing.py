from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/lot/(?P<lot_id>\w+)/$', consumers.LotBiddingConsumer.as_asgi()),
]