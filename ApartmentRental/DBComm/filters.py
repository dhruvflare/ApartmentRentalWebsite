# filters.py - Django Filters for Property Search

import django_filters
from django.db.models import Q
from .models import Property, PropertyType, FurnishingType


class PropertyFilter(django_filters.FilterSet):
    """Advanced filtering for properties"""

    # Location filters
    location = django_filters.CharFilter(method='filter_by_location')
    city = django_filters.CharFilter(field_name='address__city', lookup_expr='icontains')
    locality = django_filters.CharFilter(field_name='address__locality', lookup_expr='icontains')

    # Property characteristics
    property_type = django_filters.ModelChoiceFilter(queryset=PropertyType.objects.all())
    furnishing = django_filters.ModelChoiceFilter(queryset=FurnishingType.objects.all())
    bedrooms = django_filters.NumberFilter()
    bathrooms = django_filters.NumberFilter(field_name='bathrooms', lookup_expr='gte')

    # Area filters
    min_area = django_filters.NumberFilter(field_name='total_area_sqft', lookup_expr='gte')
    max_area = django_filters.NumberFilter(field_name='total_area_sqft', lookup_expr='lte')

    # Rent filters (from active listings)
    min_rent = django_filters.NumberFilter(method='filter_by_min_rent')
    max_rent = django_filters.NumberFilter(method='filter_by_max_rent')

    # Availability filters
    available_from = django_filters.DateFilter(field_name='available_from', lookup_expr='lte')
    immediately_available = django_filters.BooleanFilter(method='filter_immediately_available')

    # Amenities filter
    amenities = django_filters.CharFilter(method='filter_by_amenities')

    # Other filters
    preferred_tenant = django_filters.ChoiceFilter(
        choices=Property.PREFERRED_TENANT_CHOICES,
        method='filter_by_tenant_preference'
    )
    parking_required = django_filters.BooleanFilter(method='filter_parking_required')
    furnished = django_filters.BooleanFilter(method='filter_furnished')

    class Meta:
        model = Property
        fields = []

    def filter_by_location(self, queryset, name, value):
        """Filter by location (city, locality, or address)"""
        return queryset.filter(
            Q(address__city__icontains=value) |
            Q(address__locality__icontains=value) |
            Q(address__street_address__icontains=value)
        )

    def filter_by_min_rent(self, queryset, name, value):
        """Filter by minimum rent from active listings"""
        return queryset.filter(
            listings__listing_status='active',
            listings__monthly_rent__gte=value
        )

    def filter_by_max_rent(self, queryset, name, value):
        """Filter by maximum rent from active listings"""
        return queryset.filter(
            listings__listing_status='active',
            listings__monthly_rent__lte=value
        )

    def filter_immediately_available(self, queryset, name, value):
        """Filter properties available immediately"""
        if value:
            return queryset.filter(
                listings__listing_status='active',
                listings__immediately_available=True
            )
        return queryset

    def filter_by_amenities(self, queryset, name, value):
        """Filter by comma-separated amenity IDs"""
        if value:
            amenity_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
            for amenity_id in amenity_ids:
                queryset = queryset.filter(amenities__id=amenity_id)
        return queryset

    def filter_by_tenant_preference(self, queryset, name, value):
        """Filter by preferred tenant type"""
        return queryset.filter(
            Q(preferred_tenant=value) | Q(preferred_tenant='any')
        )

    def filter_parking_required(self, queryset, name, value):
        """Filter properties with parking"""
        if value:
            return queryset.filter(parking_available=True)
        return queryset

    def filter_furnished(self, queryset, name, value):
        """Filter furnished properties"""
        if value:
            return queryset.filter(
                furnishing__furnishing_type__in=['Fully Furnished', 'Semi Furnished']
            )
        else:
            return queryset.filter(furnishing__furnishing_type='Unfurnished')
        return queryset