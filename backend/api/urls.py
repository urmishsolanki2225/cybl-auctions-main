# frontapi/urls.py

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
from api import views

urlpatterns = [
    #User Register
    path('register/', views.RegisterView.as_view(), name='register'),

    #LoginPage
    path('login/', views.LoginView.as_view(), name='login'),

    #All Country Fetch
    path('countries/', views.CountryListCreateView.as_view(), name='country-list-create'),
    path('countries/<int:pk>/', views.CountryRetrieveUpdateDestroyView.as_view(), name='country-detail'),
    
    #All State Fetch
    path('states/', views.StateListCreateView.as_view(), name='state-list-create'),
    path('states/<int:pk>/', views.StateRetrieveUpdateDestroyView.as_view(), name='state-detail'),
    
    # New endpoint to fetch states by country ID
    path('countries/<int:country_id>/states/', views.StateByCountryView.as_view(), name='states-by-country'),

    #profile
    path('profile/', views.ProfileDetail.as_view(), name='profile-detail'),

    # path('profile/', views.ProfileDetail, name='profile-detail'),
    # path('change-password/', views.ChangePasswordView, name='change_password'),
    path('password/update/', views.PasswordUpdateView.as_view(), name='password-update'),
 

    # # login required tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # # items urls
    # path('items/', ItemListView, name='item_list'),
    path('lots/<int:id>/', views.InventoryDetailAPIView.as_view(), name='inventory-detail'),
    path('lots/<int:lot_id>/bid/', views.place_bid_api, name='place_bid'),
    path('lots/<int:lot_id>/bids/', views.get_bid_history, name='bid_history'),
    path('lots/<int:lot_id>/status/', views.get_lot_status, name='lot_status'),
   

  

    # # auction url
    path('auctions/', views.AuctionListView.as_view(), name='auction_view'),    
    path('auctions/<int:pk>/', views.AuctionDetailView.as_view(), name='auction_detail'),    

    # #Category
    path('categories/',  views.CategoryListView.as_view(), name='category-list-create'),
    # path('categories/<int:pk>/', CategoryDetailView, name='category-detail'),

    # #items
    # path('subcategories/<int:subcategory_id>/latest-items/', LatestItemsBySubcategoryView, name='latest-items-by-subcategory'),

    # #Compnay
    path('companies/', views.CompanyListView.as_view(), name='company-list'),

    # path('category-for-filters/', CategoryfiltersListView, name='category_list'),

    # # place_bid
    # path('items/<int:item_id>/place-bid/', place_bid, name='place_bid'),
    # path('items/<int:item_id>/latest-bid/', LatestBidView, name='latest-bid'),

    # path('user/bidding-history/', UserBiddingHistoryView, name='user-bidding-history'),
    path('user/bidding-history/', views.user_bidding_history, name='user_bidding_history'),

    path('user/payment-history/',  views.user_payment_history, name='payment-history-list'),
]