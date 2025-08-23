'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/Layout';
import FiltersSidebar from '@/components/FiltersSidebar';
import PropertyCard from '@/components/PropertyCard';
import api from '@/lib/api';
import type { Property, Filters, PropertyListResponse } from '@/types';

export default function HomePage() {
  // Use the typed Filters interface instead of any
  const [filters, setFilters] = useState<Filters>({});

  const { data, isLoading, error } = useQuery<PropertyListResponse, Error>({
    queryKey: ['properties', filters],
    queryFn: () =>
      api.get<PropertyListResponse>('properties/', { params: filters }).then(res => res.data),
  });

  if (isLoading) return <Layout>Loading…</Layout>;
  if (error) return <Layout>Error: {error.message}</Layout>;

  return (
    <Layout>
      <FiltersSidebar onChange={setFilters} />
      {data?.results.map(p => (
        <PropertyCard key={p.id} {...p} />
      ))}
    </Layout>
  );
}
