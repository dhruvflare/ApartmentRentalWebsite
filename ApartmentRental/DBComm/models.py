# models.py - Apartment Rental Django Models (FIXED)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import JSONField  # FIXED: Updated import
from django.utils import timezone


class BaseModel(models.Model):
    """Abstract base model with common fields for all models"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Address(BaseModel):
    """Address information for properties"""
    street_address = models.CharField(max_length=255)
    apartment_number = models.CharField(max_length=20, blank=True, null=True)
    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'addresses'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.street_address}, {self.locality}, {self.city}"


class Locality(BaseModel):
    """Neighborhood information for better search functionality"""
    locality_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    AREA_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('mixed', 'Mixed'),
    ]
    area_type = models.CharField(max_length=20, choices=AREA_TYPE_CHOICES, blank=True, null=True)

    connectivity_rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    safety_rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    lifestyle_rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )

    class Meta:
        db_table = 'localities'
        verbose_name = 'Locality'
        verbose_name_plural = 'Localities'

    def __str__(self):
        return f"{self.locality_name}, {self.city}"


class User(AbstractUser, BaseModel):
    """Extended User model with apartment rental specific fields"""
    USER_TYPE_CHOICES = [
        ('owner', 'Owner'),
        ('tenant', 'Tenant'),
        ('both', 'Both'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    phone_number = models.CharField(max_length=15, unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_type})"


class UserPreference(BaseModel):
    """User search and notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_locations = JSONField(default=list, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preferred_property_types = JSONField(default=list, blank=True)
    preferred_amenities = JSONField(default=list, blank=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferences for {self.user.username}"


class PropertyType(BaseModel):
    """Property type lookup table"""
    type_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'property_types'
        verbose_name = 'Property Type'
        verbose_name_plural = 'Property Types'

    def __str__(self):
        return self.type_name


class FurnishingType(BaseModel):
    """Furnishing type lookup table"""
    furnishing_type = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'furnishing_types'
        verbose_name = 'Furnishing Type'
        verbose_name_plural = 'Furnishing Types'

    def __str__(self):
        return self.furnishing_type


class Amenity(BaseModel):
    """Amenities lookup table"""
    amenity_name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    icon = models.ImageField(upload_to='amenity_icons/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'amenities'
        verbose_name = 'Amenity'
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return self.amenity_name


class Property(BaseModel):
    """Main property model"""
    CONSTRUCTION_STATUS_CHOICES = [
        ('ready_to_move', 'Ready to Move'),
        ('under_construction', 'Under Construction'),
    ]

    FACING_DIRECTION_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('north_east', 'North East'),
        ('north_west', 'North West'),
        ('south_east', 'South East'),
        ('south_west', 'South West'),
    ]

    PREFERRED_TENANT_CHOICES = [
        ('family', 'Family'),
        ('bachelor_male', 'Bachelor Male'),
        ('bachelor_female', 'Bachelor Female'),
        ('company', 'Company'),
        ('any', 'Any'),
    ]

    # Foreign Keys
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_properties')
    property_type = models.ForeignKey(PropertyType, on_delete=models.RESTRICT, related_name='properties')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='properties')
    furnishing = models.ForeignKey(
        FurnishingType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties'
    )
    amenities = models.ManyToManyField(Amenity, through='PropertyAmenity', related_name='properties')

    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # Property Details
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    total_area_sqft = models.PositiveIntegerField(blank=True, null=True)
    carpet_area_sqft = models.PositiveIntegerField(blank=True, null=True)
    floor_number = models.IntegerField(blank=True, null=True)
    total_floors = models.PositiveIntegerField(blank=True, null=True)
    age_of_property = models.PositiveIntegerField(blank=True, null=True)

    # Additional Features
    parking_available = models.BooleanField(default=False)
    parking_spaces = models.PositiveIntegerField(default=0)
    balcony_count = models.PositiveIntegerField(default=0)

    # Property Characteristics
    construction_status = models.CharField(
        max_length=20,
        choices=CONSTRUCTION_STATUS_CHOICES,
        blank=True,
        null=True
    )
    facing_direction = models.CharField(
        max_length=20,
        choices=FACING_DIRECTION_CHOICES,
        blank=True,
        null=True
    )
    preferred_tenant = models.CharField(
        max_length=20,
        choices=PREFERRED_TENANT_CHOICES,
        blank=True,
        null=True
    )

    # Availability
    available_from = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'properties'
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['property_type', 'is_active']),
            models.Index(fields=['bedrooms', 'is_active']),
            models.Index(fields=['address']),
        ]

    def __str__(self):
        return f"{self.title} - {self.property_type.type_name}"

    @property
    def primary_image(self):
        """Get the primary image for this property"""
        return self.images.filter(is_primary=True).first()


class PropertyAmenity(BaseModel):
    """Junction table for Property and Amenity many-to-many relationship"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name='property_amenities')
    available = models.BooleanField(default=True)

    class Meta:
        db_table = 'property_amenities'
        verbose_name = 'Property Amenity'
        verbose_name_plural = 'Property Amenities'
        unique_together = ('property', 'amenity')

    def __str__(self):
        return f"{self.property.title} - {self.amenity.amenity_name}"


class Listing(BaseModel):
    """Property listing with pricing information"""
    LISTING_TYPE_CHOICES = [
        ('rent', 'Rent'),
        ('sale', 'Sale'),
    ]

    LISTING_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('rented', 'Rented'),
        ('sold', 'Sold'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='listings')

    # Pricing
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    maintenance_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    brokerage_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Listing Information
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, blank=True, null=True)
    listing_status = models.CharField(max_length=20, choices=LISTING_STATUS_CHOICES, default='active')
    negotiable = models.BooleanField(default=True)
    immediately_available = models.BooleanField(default=True)

    # Dates
    listing_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(blank=True, null=True)

    # Analytics
    views_count = models.PositiveIntegerField(default=0)
    contact_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['listing_status']),
            models.Index(fields=['monthly_rent', 'listing_status']),
        ]

    def __str__(self):
        return f"{self.property.title} - ₹{self.monthly_rent}/month"


class PropertyImage(BaseModel):
    """Property images with proper organization"""
    IMAGE_TYPE_CHOICES = [
        ('main', 'Main'),
        ('bedroom', 'Bedroom'),
        ('bathroom', 'Bathroom'),
        ('kitchen', 'Kitchen'),
        ('living_room', 'Living Room'),
        ('balcony', 'Balcony'),
        ('exterior', 'Exterior'),
        ('floor_plan', 'Floor Plan'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    image_type = models.CharField(max_length=50, choices=IMAGE_TYPE_CHOICES)
    image_order = models.PositiveIntegerField(default=0)
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    file_size = models.PositiveIntegerField(blank=True, null=True)  # in bytes
    dimensions = models.CharField(max_length=20, blank=True, null=True)  # e.g., '1920x1080'

    class Meta:
        db_table = 'property_images'
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['property', 'is_primary']),
        ]
        ordering = ['image_order', 'created_at']

    def __str__(self):
        return f"{self.property.title} - {self.image_type}"


class PropertyInquiry(BaseModel):
    """Property inquiries from potential tenants"""
    INQUIRY_TYPE_CHOICES = [
        ('call', 'Call'),
        ('message', 'Message'),
        ('visit_request', 'Visit Request'),
        ('general', 'General'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='inquiries')
    inquirer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries')

    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPE_CHOICES, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    preferred_contact_time = models.CharField(max_length=50, blank=True, null=True)
    inquiry_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Owner Response
    owner_response = models.TextField(blank=True, null=True)
    response_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'property_inquiries'
        verbose_name = 'Property Inquiry'
        verbose_name_plural = 'Property Inquiries'
        indexes = [
            models.Index(fields=['property', 'inquirer']),
            models.Index(fields=['inquirer', 'inquiry_date']),
        ]

    def __str__(self):
        return f"Inquiry for {self.property.title} by {self.inquirer.username}"


class SavedProperty(BaseModel):
    """User's saved/favorite properties - Many-to-Many junction table"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='saved_by_users')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'saved_properties'
        verbose_name = 'Saved Property'
        verbose_name_plural = 'Saved Properties'
        unique_together = ('user', 'property')
        indexes = [
            models.Index(fields=['user', 'property']),
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.property.title}"


class UserSearch(BaseModel):
    """Track user search preferences for personalized recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    location = models.CharField(max_length=255, blank=True, null=True)
    min_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    max_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    bedrooms = models.PositiveIntegerField(blank=True, null=True)
    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='searches'
    )
    furnishing = models.ForeignKey(
        FurnishingType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='searches'
    )
    search_query = JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'user_searches'
        verbose_name = 'User Search'
        verbose_name_plural = 'User Searches'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(min_rent__isnull=True) |
                      models.Q(max_rent__isnull=True) |
                      models.Q(min_rent__lte=models.F('max_rent')),
                name='min_rent_lte_max_rent'
            )
        ]

    def __str__(self):
        return f"Search by {self.user.username} on {self.created_at.date()}"


class ReviewRating(BaseModel):
    """Property and owner reviews by tenants"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'reviews_ratings'
        verbose_name = 'Review & Rating'
        verbose_name_plural = 'Reviews & Ratings'
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['reviewer']),
        ]

    def __str__(self):
        return f"{self.rating}★ review for {self.property.title} by {self.reviewer.username}"


class PropertyVisit(BaseModel):
    """Track property visit schedules"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visits')
    visitor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_visits')
    visit_date = models.DateField()
    visit_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'property_visits'
        verbose_name = 'Property Visit'
        verbose_name_plural = 'Property Visits'
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['visitor']),
            models.Index(fields=['visit_date', 'status']),
        ]

    def __str__(self):
        return f"Visit to {self.property.title} by {self.visitor.username} on {self.visit_date}"


class NearbyPlace(BaseModel):
    """Points of interest near properties"""
    PLACE_TYPE_CHOICES = [
        ('metro_station', 'Metro Station'),
        ('bus_stop', 'Bus Stop'),
        ('hospital', 'Hospital'),
        ('school', 'School'),
        ('mall', 'Mall'),
        ('market', 'Market'),
        ('restaurant', 'Restaurant'),
        ('atm', 'ATM'),
        ('gym', 'Gym'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='nearby_places')
    place_type = models.CharField(max_length=30, choices=PLACE_TYPE_CHOICES, blank=True, null=True)
    place_name = models.CharField(max_length=200)
    distance_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    walk_time_minutes = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'nearby_places'
        verbose_name = 'Nearby Place'
        verbose_name_plural = 'Nearby Places'
        indexes = [
            models.Index(fields=['property']),
        ]

    def __str__(self):
        return f"{self.place_name} ({self.place_type}) near {self.property.title}"