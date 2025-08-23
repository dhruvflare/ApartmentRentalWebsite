'use client';

import { FormEvent, useState } from 'react';
import api from '@/lib/api';

interface InquiryFormProps {
  propertyId: string;
}

export default function InquiryForm({ propertyId }: InquiryFormProps) {
  const [message, setMessage] = useState<string>('');

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    await api.post('inquiries/', { property: propertyId, message });
    setMessage('');
    alert('Inquiry sent');
  };

  return (
    <form onSubmit={submit} className="mt-4">
      <h3 className="font-semibold mb-2">Send Inquiry</h3>
      <textarea
        value={message}
        onChange={e => setMessage(e.target.value)}
        className="w-full p-2 border rounded mb-2"
        placeholder="Your message"
      />
      <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
        Send
      </button>
    </form>
  );
}
