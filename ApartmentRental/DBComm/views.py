# views.py - Django REST Framework Views (FIXED)

from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.db.models import Q, Avg, Count, F
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    User, Property, PropertyType, FurnishingType, Amenity,
    Listing, PropertyImage, PropertyInquiry, SavedProperty,
    UserSearch, ReviewRating, PropertyVisit, Address
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    PropertyListSerializer, PropertyDetailSerializer, PropertyCreateUpdateSerializer,
    PropertyTypeSerializer, FurnishingTypeSerializer, AmenitySerializer,
    ListingSerializer, PropertyImageSerializer, PropertyInquirySerializer,
    SavedPropertySerializer, UserSearchSerializer, ReviewRatingSerializer,
    PropertyVisitSerializer, PropertySearchSerializer, AddressSerializer
)
from .filters import PropertyFilter
from .permissions import IsOwnerOrReadOnly, IsOwnerOnly


# Authentication Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """User logout endpoint"""
    try:
        request.user.auth_token.delete()
    except:
        pass
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Property Views
class PropertyListView(generics.ListAPIView):
    """List all active properties with search and filtering"""
    serializer_class = PropertyListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['title', 'description', 'address__locality', 'address__city']
    ordering_fields = ['created_at', 'title', 'bedrooms', 'total_area_sqft']
    ordering = ['-created_at']

    def get_queryset(self):
        return Property.objects.filter(
            is_active=True,
            listings__listing_status='active'
        ).distinct().select_related(
            'property_type', 'furnishing', 'owner', 'address'
        ).prefetch_related('images', 'listings')


class PropertyDetailView(generics.RetrieveAPIView):
    """Get detailed property information"""
    serializer_class = PropertyDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'

    def get_queryset(self):
        return Property.objects.select_related(
            'property_type', 'furnishing', 'owner', 'address'
        ).prefetch_related(
            'images', 'amenities', 'nearby_places', 'listings', 'reviews'
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count for active listings
        instance.listings.filter(listing_status='active').update(
            views_count=F('views_count') + 1
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PropertyCreateView(generics.CreateAPIView):
    """Create a new property (owners only)"""
    serializer_class = PropertyCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure user is owner or both
        if self.request.user.user_type not in ['owner', 'both']:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError("Only owners can create properties")
        serializer.save(owner=self.request.user)


class PropertyUpdateView(generics.UpdateAPIView):
    """Update property (owner only)"""
    serializer_class = PropertyCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOnly]
    lookup_field = 'pk'

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)


class PropertyDeleteView(generics.DestroyAPIView):
    """Delete property (owner only)"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOnly]
    lookup_field = 'pk'

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)


class MyPropertiesView(generics.ListAPIView):
    """List user's own properties"""
    serializer_class = PropertyListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Property.objects.filter(
            owner=self.request.user
        ).select_related('property_type', 'furnishing', 'address')


# Property Search
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def search_properties(request):
    """Advanced property search with filters"""
    search_serializer = PropertySearchSerializer(data=request.data)
    if not search_serializer.is_valid():
        return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    filters = search_serializer.validated_data
    queryset = Property.objects.filter(
        is_active=True,
        listings__listing_status='active'
    ).distinct()

    # Apply filters
    if filters.get('location'):
        location = filters['location']
        queryset = queryset.filter(
            Q(address__locality__icontains=location) |
            Q(address__city__icontains=location) |
            Q(address__state__icontains=location)
        )

    if filters.get('property_type'):
        queryset = queryset.filter(property_type_id=filters['property_type'])

    if filters.get('furnishing'):
        queryset = queryset.filter(furnishing_id=filters['furnishing'])

    if filters.get('bedrooms'):
        queryset = queryset.filter(bedrooms=filters['bedrooms'])

    if filters.get('bathrooms'):
        queryset = queryset.filter(bathrooms__gte=filters['bathrooms'])

    if filters.get('min_area'):
        queryset = queryset.filter(total_area_sqft__gte=filters['min_area'])

    if filters.get('max_area'):
        queryset = queryset.filter(total_area_sqft__lte=filters['max_area'])

    if filters.get('preferred_tenant'):
        queryset = queryset.filter(
            Q(preferred_tenant=filters['preferred_tenant']) |
            Q(preferred_tenant='any')
        )

    if filters.get('parking_required'):
        queryset = queryset.filter(parking_available=True)

    if filters.get('available_from'):
        queryset = queryset.filter(available_from__lte=filters['available_from'])

    # Filter by rent range
    if filters.get('min_rent') or filters.get('max_rent'):
        listing_filters = {}
        if filters.get('min_rent'):
            listing_filters['listings__monthly_rent__gte'] = filters['min_rent']
        if filters.get('max_rent'):
            listing_filters['listings__monthly_rent__lte'] = filters['max_rent']
        queryset = queryset.filter(**listing_filters)

    # Filter by amenities
    if filters.get('amenities'):
        for amenity_id in filters['amenities']:
            queryset = queryset.filter(amenities__id=amenity_id)

    # Save search if user is authenticated
    if request.user.is_authenticated:
        UserSearch.objects.create(
            user=request.user,
            location=filters.get('location', ''),
            min_rent=filters.get('min_rent'),
            max_rent=filters.get('max_rent'),
            bedrooms=filters.get('bedrooms'),
            property_type_id=filters.get('property_type'),
            furnishing_id=filters.get('furnishing'),
            search_query=filters
        )

    # Serialize results
    properties = queryset.select_related(
        'property_type', 'furnishing', 'owner', 'address'
    ).prefetch_related('images', 'listings')[:50]  # Limit to 50 results

    serializer = PropertyListSerializer(properties, many=True)
    return Response({
        'count': len(properties),
        'results': serializer.data
    })


# Listing Views
class ListingViewSet(ModelViewSet):
    """CRUD operations for property listings"""
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type in ['owner', 'both']:
            return Listing.objects.filter(property__owner=self.request.user)
        return Listing.objects.none()

    def perform_create(self, serializer):
        property_id = self.request.data.get('property')
        try:
            property_obj = Property.objects.get(id=property_id, owner=self.request.user)
            serializer.save(property=property_obj)
        except Property.DoesNotExist:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError("Property not found or not owned by user")


# Property Inquiry Views
class PropertyInquiryCreateView(generics.CreateAPIView):
    """Create property inquiry"""
    serializer_class = PropertyInquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        property_id = self.request.data.get('property')
        listing_id = self.request.data.get('listing')

        # Increment contact count for the listing
        try:
            listing = Listing.objects.get(id=listing_id)
            listing.contact_count += 1
            listing.save()
        except Listing.DoesNotExist:
            pass

        serializer.save(
            inquirer=self.request.user,
            inquiry_date=timezone.now()
        )


class MyInquiriesView(generics.ListAPIView):
    """List user's inquiries"""
    serializer_class = PropertyInquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PropertyInquiry.objects.filter(
            inquirer=self.request.user
        ).select_related('property', 'listing').order_by('-inquiry_date')


class ReceivedInquiriesView(generics.ListAPIView):
    """List inquiries received for user's properties"""
    serializer_class = PropertyInquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PropertyInquiry.objects.filter(
            property__owner=self.request.user
        ).select_related('property', 'listing', 'inquirer').order_by('-inquiry_date')


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def respond_to_inquiry(request, inquiry_id):
    """Respond to property inquiry"""
    try:
        inquiry = PropertyInquiry.objects.get(
            id=inquiry_id,
            property__owner=request.user
        )
        inquiry.owner_response = request.data.get('response', '')
        inquiry.status = 'responded'
        inquiry.response_date = timezone.now()
        inquiry.save()

        serializer = PropertyInquirySerializer(inquiry)
        return Response(serializer.data)
    except PropertyInquiry.DoesNotExist:
        return Response({'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)


# Saved Properties Views
class SavedPropertiesView(generics.ListCreateAPIView):
    """List and create saved properties"""
    serializer_class = SavedPropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedProperty.objects.filter(
            user=self.request.user
        ).select_related('property')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_saved_property(request, property_id):
    """Remove property from saved list"""
    try:
        saved_property = SavedProperty.objects.get(
            user=request.user,
            property_id=property_id
        )
        saved_property.delete()
        return Response({'message': 'Property removed from saved list'})
    except SavedProperty.DoesNotExist:
        return Response({'error': 'Saved property not found'}, status=status.HTTP_404_NOT_FOUND)


# Reviews and Ratings
class ReviewRatingCreateView(generics.CreateAPIView):
    """Create property review and rating"""
    serializer_class = ReviewRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class PropertyReviewsView(generics.ListAPIView):
    """List reviews for a property"""
    serializer_class = ReviewRatingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        property_id = self.kwargs['property_id']
        return ReviewRating.objects.filter(
            property_id=property_id
        ).select_related('reviewer').order_by('-created_at')


# Property Visits
class PropertyVisitCreateView(generics.CreateAPIView):
    """Schedule property visit"""
    serializer_class = PropertyVisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(visitor=self.request.user)


class MyVisitsView(generics.ListAPIView):
    """List user's scheduled visits"""
    serializer_class = PropertyVisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PropertyVisit.objects.filter(
            visitor=self.request.user
        ).select_related('property').order_by('visit_date', 'visit_time')


# Lookup Tables Views
class PropertyTypeListView(generics.ListAPIView):
    """List all property types"""
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [permissions.AllowAny]


class FurnishingTypeListView(generics.ListAPIView):
    """List all furnishing types"""
    queryset = FurnishingType.objects.all()
    serializer_class = FurnishingTypeSerializer
    permission_classes = [permissions.AllowAny]


class AmenityListView(generics.ListAPIView):
    """List all amenities"""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.AllowAny]


# Property Images
class PropertyImageCreateView(generics.CreateAPIView):
    """Upload property image"""
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        property_id = self.request.data.get('property')
        try:
            property_obj = Property.objects.get(id=property_id, owner=self.request.user)
            serializer.save(property=property_obj)
        except Property.DoesNotExist:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError("Property not found or not owned by user")


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_property_image(request, image_id):
    """Delete property image"""
    try:
        image = PropertyImage.objects.get(
            id=image_id,
            property__owner=request.user
        )
        image.delete()
        return Response({'message': 'Image deleted successfully'})
    except PropertyImage.DoesNotExist:
        return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)


# Dashboard/Analytics Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def owner_dashboard(request):
    """Owner dashboard with analytics"""
    if request.user.user_type not in ['owner', 'both']:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    properties = Property.objects.filter(owner=request.user)

    stats = {
        'total_properties': properties.count(),
        'active_properties': properties.filter(is_active=True).count(),
        'total_listings': Listing.objects.filter(property__owner=request.user).count(),
        'active_listings': Listing.objects.filter(
            property__owner=request.user,
            listing_status='active'
        ).count(),
        'total_inquiries': PropertyInquiry.objects.filter(
            property__owner=request.user
        ).count(),
        'pending_inquiries': PropertyInquiry.objects.filter(
            property__owner=request.user,
            status='pending'
        ).count(),
        'total_views': Listing.objects.filter(
            property__owner=request.user
        ).aggregate(total=Count('views_count'))['total'] or 0,
        'total_contacts': Listing.objects.filter(
            property__owner=request.user
        ).aggregate(total=Count('contact_count'))['total'] or 0,
    }

    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def tenant_dashboard(request):
    """Tenant dashboard"""
    stats = {
        'saved_properties': SavedProperty.objects.filter(user=request.user).count(),
        'inquiries_made': PropertyInquiry.objects.filter(inquirer=request.user).count(),
        'scheduled_visits': PropertyVisit.objects.filter(
            visitor=request.user,
            status='scheduled'
        ).count(),
        'reviews_given': ReviewRating.objects.filter(reviewer=request.user).count(),
    }

    # Recent searches
    recent_searches = UserSearch.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    return Response({
        'stats': stats,
        'recent_searches': UserSearchSerializer(recent_searches, many=True).data
    })