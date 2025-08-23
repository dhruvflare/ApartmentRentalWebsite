'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { Review } from '@/types';

interface ReviewListProps {
  propertyId: string;
}

export default function ReviewList({ propertyId }: ReviewListProps) {
  const { data: reviews, isLoading, error } = useQuery<Review[], Error>({
    queryKey: ['reviews', propertyId],
    queryFn: () =>
      api
        .get<Review[]>(`properties/${propertyId}/reviews/`)
        .then(res => res.data),
  });

  if (isLoading) {
    return <p>Loading reviews…</p>;
  }

  if (error) {
    return <p className="text-red-500">Error loading reviews: {error.message}</p>;
  }

  if (!reviews || reviews.length === 0) {
    return <p>No reviews yet.</p>;
  }

  return (
    <div>
      <h3 className="font-semibold mt-4">Reviews</h3>
      {reviews.map(r => (
        <div key={r.id} className="border-b py-2">
          <p className="font-medium">{r.reviewer.username}</p>
          <p>Rating: {r.rating}/5</p>
          <p>{r.review_text}</p>
        </div>
      ))}
    </div>
  );
}
