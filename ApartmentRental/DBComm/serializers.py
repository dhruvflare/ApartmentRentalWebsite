# serializers.py - Django REST Framework Serializers

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, UserPreference, Property, PropertyType, FurnishingType,
    Amenity, PropertyAmenity, Listing, PropertyImage, PropertyInquiry,
    SavedProperty, UserSearch, ReviewRating, PropertyVisit, NearbyPlace, Address
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'user_type',
            'date_of_birth', 'gender', 'occupation'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'user_type', 'profile_picture',
            'date_of_birth', 'gender', 'occupation', 'is_verified', 'status'
        )
        read_only_fields = ('id', 'username', 'is_verified', 'status')


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for addresses"""

    class Meta:
        model = Address
        fields = '__all__'


class PropertyTypeSerializer(serializers.ModelSerializer):
    """Serializer for property types"""

    class Meta:
        model = PropertyType
        fields = '__all__'


class FurnishingTypeSerializer(serializers.ModelSerializer):
    """Serializer for furnishing types"""

    class Meta:
        model = FurnishingType
        fields = '__all__'


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for amenities"""

    class Meta:
        model = Amenity
        fields = '__all__'


class PropertyImageSerializer(serializers.ModelSerializer):
    """Serializer for property images"""

    class Meta:
        model = PropertyImage
        fields = '__all__'


class NearbyPlaceSerializer(serializers.ModelSerializer):
    """Serializer for nearby places"""

    class Meta:
        model = NearbyPlace
        fields = '__all__'


class PropertyAmenitySerializer(serializers.ModelSerializer):
    """Serializer for property amenities junction table"""
    amenity_name = serializers.CharField(source='amenity.amenity_name', read_only=True)

    class Meta:
        model = PropertyAmenity
        fields = ('amenity', 'amenity_name', 'available')


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for property listings"""

    class Meta:
        model = Listing
        fields = '__all__'


class PropertyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for property listings (list view)"""
    property_type_name = serializers.CharField(source='property_type.type_name', read_only=True)
    furnishing_type_name = serializers.CharField(source='furnishing.furnishing_type', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    current_listing = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Property
        fields = (
            'id', 'title', 'property_type_name', 'furnishing_type_name',
            'bedrooms', 'bathrooms', 'total_area_sqft', 'address',
            'owner_name', 'primary_image', 'current_listing', 'available_from'
        )

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return PropertyImageSerializer(primary_image).data
        return None

    def get_current_listing(self, obj):
        active_listing = obj.listings.filter(listing_status='active').first()
        if active_listing:
            return {
                'id': active_listing.id,
                'monthly_rent': active_listing.monthly_rent,
                'security_deposit': active_listing.security_deposit,
                'negotiable': active_listing.negotiable
            }
        return None


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual property view"""
    property_type = PropertyTypeSerializer(read_only=True)
    furnishing = FurnishingTypeSerializer(read_only=True)
    owner = UserProfileSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    amenities = serializers.SerializerMethodField()
    nearby_places = NearbyPlaceSerializer(many=True, read_only=True)
    listings = ListingSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

    def get_amenities(self, obj):
        property_amenities = obj.property_amenities.select_related('amenity')
        return PropertyAmenitySerializer(property_amenities, many=True).data

    def get_reviews(self, obj):
        reviews = obj.reviews.select_related('reviewer')[:5]  # Latest 5 reviews
        return ReviewRatingSerializer(reviews, many=True).data

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return None


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating properties"""
    amenities = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Property
        exclude = ('owner',)  # Owner will be set in the view

    def create(self, validated_data):
        amenities_data = validated_data.pop('amenities', [])
        property_instance = Property.objects.create(**validated_data)

        # Handle amenities
        for amenity in amenities_data:
            PropertyAmenity.objects.create(
                property=property_instance,
                amenity=amenity,
                available=True
            )

        return property_instance

    def update(self, instance, validated_data):
        amenities_data = validated_data.pop('amenities', None)

        # Update property fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update amenities if provided
        if amenities_data is not None:
            instance.property_amenities.all().delete()
            for amenity in amenities_data:
                PropertyAmenity.objects.create(
                    property=instance,
                    amenity=amenity,
                    available=True
                )

        return instance


class PropertyInquirySerializer(serializers.ModelSerializer):
    """Serializer for property inquiries"""
    inquirer_name = serializers.CharField(source='inquirer.get_full_name', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = PropertyInquiry
        fields = '__all__'
        read_only_fields = ('inquirer', 'inquiry_date')


class SavedPropertySerializer(serializers.ModelSerializer):
    """Serializer for saved properties"""
    property = PropertyListSerializer(read_only=True)

    class Meta:
        model = SavedProperty
        fields = '__all__'
        read_only_fields = ('user',)


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for user searches"""
    property_type_name = serializers.CharField(source='property_type.type_name', read_only=True)
    furnishing_type_name = serializers.CharField(source='furnishing.furnishing_type', read_only=True)

    class Meta:
        model = UserSearch
        fields = '__all__'
        read_only_fields = ('user',)


class ReviewRatingSerializer(serializers.ModelSerializer):
    """Serializer for reviews and ratings"""
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = ReviewRating
        fields = '__all__'
        read_only_fields = ('reviewer',)


class PropertyVisitSerializer(serializers.ModelSerializer):
    """Serializer for property visits"""
    visitor_name = serializers.CharField(source='visitor.get_full_name', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = PropertyVisit
        fields = '__all__'
        read_only_fields = ('visitor',)


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user preferences"""

    class Meta:
        model = UserPreference
        fields = '__all__'
        read_only_fields = ('user',)


# Search and Filter Serializers
class PropertySearchSerializer(serializers.Serializer):
    """Serializer for property search parameters"""
    location = serializers.CharField(required=False)
    property_type = serializers.IntegerField(required=False)
    furnishing = serializers.IntegerField(required=False)
    min_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    bedrooms = serializers.IntegerField(required=False)
    bathrooms = serializers.IntegerField(required=False)
    min_area = serializers.IntegerField(required=False)
    max_area = serializers.IntegerField(required=False)
    amenities = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    preferred_tenant = serializers.CharField(required=False)
    parking_required = serializers.BooleanField(required=False)
    available_from = serializers.DateField(required=False)

    def validate(self, attrs):
        min_rent = attrs.get('min_rent')
        max_rent = attrs.get('max_rent')

        if min_rent and max_rent and min_rent > max_rent:
            raise serializers.ValidationError("Min rent cannot be greater than max rent")

        min_area = attrs.get('min_area')
        max_area = attrs.get('max_area')

        if min_area and max_area and min_area > max_area:
            raise serializers.ValidationError("Min area cannot be greater than max area")

        return attrs