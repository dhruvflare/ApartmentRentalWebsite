# admin.py - Django Admin Configuration (FIXED)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Address, Property, PropertyType, FurnishingType,
    Amenity, PropertyAmenity, Listing, PropertyImage,
    PropertyInquiry, SavedProperty, UserSearch, ReviewRating,
    PropertyVisit, NearbyPlace, UserPreference
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'status')
    list_filter = ('user_type', 'is_verified', 'status', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'user_type', 'profile_picture',
                       'date_of_birth', 'gender', 'occupation', 'is_verified', 'status')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'user_type', 'email', 'first_name', 'last_name')
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'locality', 'city', 'state', 'pincode')
    list_filter = ('city', 'state')
    search_fields = ('street_address', 'locality', 'city', 'pincode')


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'description')
    search_fields = ('type_name',)


@admin.register(FurnishingType)
class FurnishingTypeAdmin(admin.ModelAdmin):
    list_display = ('furnishing_type', 'description')
    search_fields = ('furnishing_type',)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('amenity_name', 'category')
    list_filter = ('category',)
    search_fields = ('amenity_name',)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'image_type', 'is_primary', 'caption')


class PropertyAmenityInline(admin.TabularInline):
    model = PropertyAmenity
    extra = 1


class ListingInline(admin.TabularInline):
    model = Listing
    extra = 1
    fields = ('monthly_rent', 'security_deposit', 'listing_status', 'negotiable')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'property_type', 'bedrooms', 'bathrooms',
                    'get_location', 'is_active', 'created_at')
    list_filter = ('property_type', 'furnishing', 'is_active', 'bedrooms', 'construction_status')
    search_fields = ('title', 'owner__username', 'address__locality', 'address__city')
    date_hierarchy = 'created_at'

    inlines = [PropertyImageInline, PropertyAmenityInline, ListingInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'title', 'description', 'property_type', 'address')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'total_area_sqft', 'carpet_area_sqft',
                       'floor_number', 'total_floors', 'age_of_property')
        }),
        ('Features', {
            'fields': ('furnishing', 'parking_available', 'parking_spaces',
                       'balcony_count', 'construction_status', 'facing_direction')
        }),
        ('Availability', {
            'fields': ('preferred_tenant', 'available_from', 'is_active')
        })
    )

    def get_location(self, obj):
        return f"{obj.address.locality}, {obj.address.city}"

    get_location.short_description = 'Location'


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('property', 'monthly_rent', 'listing_status', 'listing_type',
                    'negotiable', 'views_count', 'contact_count', 'listing_date')
    list_filter = ('listing_status', 'listing_type', 'negotiable', 'immediately_available')
    search_fields = ('property__title', 'property__owner__username')
    date_hierarchy = 'listing_date'

    fieldsets = (
        ('Property & Status', {
            'fields': ('property', 'listing_type', 'listing_status')
        }),
        ('Pricing', {
            'fields': ('monthly_rent', 'security_deposit', 'maintenance_charges', 'brokerage_fee')
        }),
        ('Availability', {
            'fields': ('negotiable', 'immediately_available', 'expiry_date')
        }),
        ('Analytics', {
            'fields': ('views_count', 'contact_count')
        })
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    # FIXED: Using 'created_at' instead of 'uploaded_at'
    list_display = ('property', 'image_type', 'is_primary', 'image_preview', 'created_at')
    list_filter = ('image_type', 'is_primary')
    search_fields = ('property__title',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;"/>', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'


@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    list_display = ('property', 'inquirer', 'inquiry_type', 'status', 'inquiry_date')
    list_filter = ('inquiry_type', 'status', 'inquiry_date')
    search_fields = ('property__title', 'inquirer__username', 'message')
    date_hierarchy = 'inquiry_date'

    fieldsets = (
        ('Inquiry Details', {
            'fields': ('property', 'listing', 'inquirer', 'inquiry_type', 'message')
        }),
        ('Contact Preference', {
            'fields': ('preferred_contact_time',)
        }),
        ('Response', {
            'fields': ('status', 'owner_response', 'response_date')
        })
    )


@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    # FIXED: Using 'created_at' instead of 'saved_at'
    list_display = ('user', 'property', 'created_at')
    search_fields = ('user__username', 'property__title')
    date_hierarchy = 'created_at'


@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    # FIXED: Using 'created_at' instead of 'review_date'
    list_display = ('property', 'reviewer', 'rating', 'is_verified', 'created_at')
    list_filter = ('rating', 'is_verified', 'created_at')
    search_fields = ('property__title', 'reviewer__username', 'review_text')
    date_hierarchy = 'created_at'


@admin.register(PropertyVisit)
class PropertyVisitAdmin(admin.ModelAdmin):
    list_display = ('property', 'visitor', 'visit_date', 'visit_time', 'status')
    list_filter = ('status', 'visit_date')
    search_fields = ('property__title', 'visitor__username')
    date_hierarchy = 'visit_date'


@admin.register(UserSearch)
class UserSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'min_rent', 'max_rent', 'bedrooms', 'created_at')
    list_filter = ('bedrooms', 'property_type', 'created_at')
    search_fields = ('user__username', 'location')
    date_hierarchy = 'created_at'


@admin.register(NearbyPlace)
class NearbyPlaceAdmin(admin.ModelAdmin):
    list_display = ('property', 'place_name', 'place_type', 'distance_km')
    list_filter = ('place_type',)
    search_fields = ('property__title', 'place_name')


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'budget_min', 'budget_max', 'email_notifications', 'sms_notifications')
    search_fields = ('user__username',)