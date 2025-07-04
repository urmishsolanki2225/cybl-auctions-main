# backend\api\urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
from api import views

urlpatterns = [
    # USER REGISTER
    path('register/google/', views.GoogleRegisterView.as_view(), name='google_register'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # LOGIN
    path('login/', views.LoginView.as_view(), name='login'),
    path('login/google/', views.GoogleLoginView.as_view(), name='google_login'),  # Add this lines

    # ALL COUNTRY + DETAILS
    path('countries/', views.CountryListCreateView.as_view(), name='country-list-create'),
    path('countries/<int:pk>/', views.CountryRetrieveUpdateDestroyView.as_view(), name='country-detail'),
    
    # ALL STATES + DETAILS
    path('states/', views.StateListCreateView.as_view(), name='state-list-create'),
    path('states/<int:pk>/', views.StateRetrieveUpdateDestroyView.as_view(), name='state-detail'),
    
    # New endpoint to fetch states by country ID
    path('countries/<int:country_id>/states/', views.StateByCountryView.as_view(), name='states-by-country'),

    # PROFILE
    path('profile/', views.ProfileDetail.as_view(), name='profile-detail'),

    # PASSWORD UPDATE
    path('password/update/', views.PasswordUpdateView.as_view(), name='password-update'), 

    #Login required tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #LOT URLS
    path('lots/<int:id>/', views.InventoryDetailAPIView.as_view(), name='inventory-detail'),
    # path('lots/<int:lot_id>/bid/', views.place_bid_api, name='place_bid'),
    # path('lots/<int:lot_id>/bids/', views.get_bid_history, name='bid_history'),
    # path('lots/<int:lot_id>/status/', views.get_lot_status, name='lot_status'),   

    # AUCTIONS
    path('auctions/', views.AuctionListView.as_view(), name='auction_view'),   
    path('auctions/closing-soon/',  views.ClosingSoonAuctionsView.as_view(), name='closing-soon-auctions'),


    # AUCTIONS DETAILS 
    path('auctions/<int:pk>/', views.AuctionDetailView.as_view(), name='auction_detail'),    

    #CETEGORY WISE LOTS :
    path('lots/',  views.CategoryLotsView.as_view(), name='category-lots'),

    # CATEGORIES
    path('categories/',  views.CategoryListView.as_view(), name='category-list-create'),
    path('categories/<int:parent_id>/', views.SubcategoryListView.as_view(), name='subcategory-list'),


    # COMPANY
    path('companies/', views.CompanyListView.as_view(), name='company-list'),

    # BIDDING HISTORY
    path('user/bidding-history/', views.user_bidding_history, name='user_bidding_history'),

    # PAYMENT HISTORY
    path('user/payment-history/',  views.user_payment_history, name='payment-history-list'),

    #CONTACT
    path('contact/', views.ContactFormView.as_view(), name='contact-form'),

    #PAYMENT INVOICE DOWBLOAD
    path('payments/<int:payment_id>/invoice/',  views.download_invoice, name='download-invoice'),

    #WATCHLIST
    path('watchlist/', views.WatchlistAPIView.as_view(), name='watchlist-list'),
    path('watchlist/add/<int:inventory_id>/', views.WatchlistAPIView.as_view(), name='watchlist-add'),
    path('watchlist/remove/<int:inventory_id>/', views.WatchlistAPIView.as_view(), name='watchlist-remove'),
    
    #LOT COMMENTS
    path('lots/<int:lot_id>/comments/', views.LotCommentsView.as_view(), name='lot-comments'),
    
    #Active Lots
    path('lots/active/', views.ActiveLotsView.as_view(), name='active-lots'),
    
    
    
    ###########################################################################################################
    #SELLER DASHBOARD
    path('seller_inventory/<int:seller_id>/', views.seller_inventory),
    path('item_bid_history/<int:item_id>/', views.item_bid_history),
    ############################################################################################################

]