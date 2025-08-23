'use client';

import { useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { AuthContext } from '@/components/AuthContext';

export default function CreatePropertyPage() {
  const { user } = useContext(AuthContext);
  const [form, setForm] = useState({ /* fields */ });
  const [images, setImages] = useState<File[]>([]);
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const fd = new FormData();
    Object.entries(form).forEach(([k, v]) => fd.append(k, v as string));
    images.forEach(file => fd.append('images', file));
    await api.post('properties/create/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    router.push('/');
  };

  if (!user) return <Layout>Redirecting to login…</Layout>;

  return (
    <Layout>
      <form onSubmit={onSubmit}>
        {/* inputs */}
        <input type="file" multiple onChange={e => setImages(Array.from(e.target.files || []))} />
        <button type="submit">Create</button>
      </form>
    </Layout>
  );
}
