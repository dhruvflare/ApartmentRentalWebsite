# urls.py - URL Configuration for DBComm app

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename='listing')

app_name = 'dbcomm'

urlpatterns = [
    # Authentication URLs
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/profile/', views.user_profile, name='profile'),
    path('auth/profile/update/', views.update_profile, name='update_profile'),

    # Property URLs
    path('properties/', views.PropertyListView.as_view(), name='property_list'),
    path('properties/search/', views.search_properties, name='property_search'),
    path('properties/create/', views.PropertyCreateView.as_view(), name='property_create'),
    path('properties/my/', views.MyPropertiesView.as_view(), name='my_properties'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('properties/<int:pk>/update/', views.PropertyUpdateView.as_view(), name='property_update'),
    path('properties/<int:pk>/delete/', views.PropertyDeleteView.as_view(), name='property_delete'),

    # Property Images URLs
    path('property-images/', views.PropertyImageCreateView.as_view(), name='property_image_create'),
    path('property-images/<int:image_id>/delete/', views.delete_property_image, name='property_image_delete'),

    # Property Inquiry URLs
    path('inquiries/', views.PropertyInquiryCreateView.as_view(), name='inquiry_create'),
    path('inquiries/my/', views.MyInquiriesView.as_view(), name='my_inquiries'),
    path('inquiries/received/', views.ReceivedInquiriesView.as_view(), name='received_inquiries'),
    path('inquiries/<int:inquiry_id>/respond/', views.respond_to_inquiry, name='respond_inquiry'),

    # Saved Properties URLs
    path('saved-properties/', views.SavedPropertiesView.as_view(), name='saved_properties'),
    path('saved-properties/<int:property_id>/remove/', views.remove_saved_property, name='remove_saved_property'),

    # Reviews and Ratings URLs
    path('reviews/', views.ReviewRatingCreateView.as_view(), name='review_create'),
    path('properties/<int:property_id>/reviews/', views.PropertyReviewsView.as_view(), name='property_reviews'),

    # Property Visits URLs
    path('visits/', views.PropertyVisitCreateView.as_view(), name='visit_create'),
    path('visits/my/', views.MyVisitsView.as_view(), name='my_visits'),

    # Lookup Tables URLs
    path('property-types/', views.PropertyTypeListView.as_view(), name='property_types'),
    path('furnishing-types/', views.FurnishingTypeListView.as_view(), name='furnishing_types'),
    path('amenities/', views.AmenityListView.as_view(), name='amenities'),

    # Dashboard URLs
    path('dashboard/owner/', views.owner_dashboard, name='owner_dashboard'),
    path('dashboard/tenant/', views.tenant_dashboard, name='tenant_dashboard'),

    # Include router URLs for ViewSets
    path('', include(router.urls)),
]