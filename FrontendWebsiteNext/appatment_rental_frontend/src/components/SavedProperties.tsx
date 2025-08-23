'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import Link from 'next/link';
import { Property } from '@/types';

interface SavedProperty {
  property: Property;
}

export default function SavedProperties() {
  const qc = useQueryClient();

  const { data, isLoading, error } = useQuery<SavedProperty[], Error>({
    queryKey: ['saved'],
    queryFn: () =>
      api.get<SavedProperty[]>('saved-properties/').then(res => res.data),
  });

  const remove = useMutation({
  mutationFn: (id: number) => api.delete(`saved-properties/${id}/remove/`),
  onSuccess: () => qc.invalidateQueries({ queryKey: ['saved'] }),
});


  if (isLoading) return <p>Loading saved properties…</p>;

  if (error)
    return <p className="text-red-500">Error loading saved properties: {error.message}</p>;

  if (!data || data.length === 0) return <p>No saved properties.</p>;

  return (
    <div>
      <h3 className="font-semibold">Your Saved Properties</h3>
      {data.map(p => (
        <div
          key={p.property.id}
          className="flex justify-between items-center border-b py-2"
        >
          <Link href={`/properties/${p.property.id}`}>
            <a>{p.property.title}</a>
          </Link>
          <button
            onClick={() => remove.mutate(p.property.id)}
            className="text-red-500"
          >
            Remove
          </button>
        </div>
      ))}
    </div>
  );
}
