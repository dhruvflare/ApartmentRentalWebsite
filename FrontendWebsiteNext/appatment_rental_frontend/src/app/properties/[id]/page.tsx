'use client';

import { useContext, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/Layout';
import ReviewList from '@/components/ReviewList';
import InquiryForm from '@/components/InquiryForm';
import api from '@/lib/api';
import { AuthContext } from '@/components/AuthContext';

export default function PropertyDetailPage() {
  const { user } = useContext(AuthContext);
  const router = useRouter();
  const id = usePathname().split('/')[2];

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  const { data } = useQuery({
    queryKey: ['property', id],
    queryFn: () => api.get(`properties/${id}/`).then(res => res.data),
    enabled: !!user,
  });

  if (!user) return <Layout>Redirecting to login…</Layout>;
  if (!data) return <Layout>Loading…</Layout>;
  return (
    <Layout>
      {/* images carousel */}
      <h1>{data.title}</h1>
      <p>{data.description}</p>
      <ReviewList propertyId={id} />
      <InquiryForm propertyId={id} />
    </Layout>
  );
}
