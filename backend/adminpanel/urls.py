from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from adminpanel.views import redirect_login

urlpatterns = [
    #Auth User
    path('',redirect_login),
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('myprofile/', views.my_profile, name='myprofile'),

    #Password Reset
    path('forget-password', views.forget_password, name='forget-password'),
    path('reset-password/done', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(template_name='login.html'), name='password_reset_complete'),

    #Users URL
    path('users/<int:tab_id>', views.all_users, name='allusers'),
    path('users/create', views.create_users, name='createusers'),
    path('users/edit/<int:user_id>', views.edit_user, name='editusers'),
    path('users/delete', views.delete_user, name='deleteuser'),
    path('fetch_states',views.fetch_states, name='fetch_states'),    
    path('users/change-password', views.change_password, name='change_password'),   

    #Category URL
    path('category/', views.all_category, name='allcategory'),
    path('category/create', views.create_category, name='createcategory'),
    path('category/edit', views.update_category, name='updatecategory'),
    path('category/delete', views.delete_category, name='deletecategory'),
    path('get_category', views.get_category, name='get_category'),
    path('fetch_categories', views.fetch_categories, name='fetch_categories'),
    path('update_category_order', views.update_category_order, name='update_category_order'),

    # Auctions
    path('auctions/<int:tabId>/', views.all_auctions, name='allauctions'),
    path('auctions/create', views.create_auction, name='createauction'),
    path('auctions/delete', views.delete_auction, name='deleteauction'),
    path('auctions/edit/<int:auction_id>/', views.edit_auction, name='editauction'),

    #Get comapany Details
    path('get-company-details', views.get_company_details, name='get_company_details'),

    # Item Transafer to Auction
    path('transfer-inventory', views.transfer_inventory, name='transfer_inventory'),
    # Auction Item Display
    path('auction-inventory/', views.auction_inventory, name='auction-inventory'),
    path('remove_inventory_from_auction/', views.remove_inventory_from_auction, name='remove_inventory_from_auction'),


    #Inventory
    path('inventory/<int:tabId>', views.all_inventory, name='allinventory'),
    path('inventory/create', views.create_inventory, name='createinventory'),
    path('inventory/edit/<int:inventory_id>/', views.edit_inventory, name='editinventory'),
    path('inventory/delete', views.delete_inventory, name='deleteinventory'),
    # In auction Bidding History Fetch    
    path('inventory/bidding-history/<int:inventory_id>', views.bidding_history, name='biddinghistory'),

    #Image
    path('inventory/upload-images/<int:inventory_id>/', views.upload_images, name='upload_images'),
    path('update-image-order/<int:inventory_id>/', views.update_image_order, name='update_image_order'),
    path('inventory/delete-image/<int:inventory_id>/', views.delete_image, name='delete_image'),


    #Roles url
    path('roles/', views.groups_index, name='groups'),
    path('roles/add/', views.add_group, name='creategroup'),
    path('roles/edit/<int:group_id>/', views.edit_group, name='editgroup'),
    path('roles/delete/', views.delete_group, name='deletegroup'),
    path('roles/view_permissions/<int:group_id>/', views.view_permissions, name='view_permissions'),
    path('roles/view_permissions/<int:group_id>/delete_permission/<int:permission_id>/', views.delete_permission, name='deletepermission'),

    #New permissions
    path('permissions/', views.permissions_management, name='permissions_management'),
    path('update_permissions/', views.update_permissions, name='update_permissions'),


    # Payment History List/Index
    path('payments/', views.payment_history_index, name='payment_history'),
    path('payments/<int:tabId>/', views.payment_history_index, name='payment_history'),
    
    # Create Payment History
    path('payments/create/', views.create_payment_history, name='createpaymenthistory'),
    
    # Edit Payment History
    path('payments/edit/<int:payment_id>/', views.edit_payment_history, name='editpaymenthistory'),
    
    # Delete Payment History (Soft Delete)
    path('payments/delete', views.delete_payment_history, name='deletepaymenthistory'),
    
    # Invoice View
    path('payments/invoice/<int:payment_id>/', views.InvoiceView, name='payment_invoice'),
    
    # AJAX endpoints for getting details
    path('ajax/inventory/<int:inventory_id>/', views.get_inventory_details, name='get_inventory_details'),
    path('ajax/user/<int:user_id>/', views.get_user_details, name='get_user_details'),




    #__cached__
    path('clear-cache/', views.clear_cache_view, name='clear_cache'),


]