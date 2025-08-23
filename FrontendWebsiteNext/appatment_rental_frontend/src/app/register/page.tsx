'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

const initialForm = {
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
  phone_number: '',
  user_type: 'tenant',
  date_of_birth: '',
  gender: 'male',
  occupation: '',
};

interface AxiosErrorResponse {
  response?: {
    data?: Record<string, string[] | string>;
  };
}

export default function RegisterPage() {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.post('auth/register/', form);
      router.push('/login');
    } catch (err: unknown) {
      let msg = 'Registration failed. Please check your details.';
      const errorObj = err as AxiosErrorResponse;
      if (errorObj.response?.data && typeof errorObj.response.data === 'object') {
        msg = Object.values(errorObj.response.data)
          .flat()
          .join(' ');
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  return (
    <div className="flex min-h-[70vh] items-center justify-center bg-gray-50">
      <form
        onSubmit={onSubmit}
        className="bg-white shadow-lg rounded-xl p-8 w-full max-w-md flex flex-col gap-4"
      >
        <h1 className="text-2xl font-bold text-blue-700 mb-2 text-center">
          Create your account
        </h1>
        {error && (
          <div className="bg-red-100 text-red-700 p-2 rounded text-sm">
            {error}
          </div>
        )}
        <label className="block">
          <span className="text-gray-700">Username</span>
          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
            required
            autoFocus
          />
        </label>
        <label className="block">
          <span className="text-gray-700">Email</span>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
            required
          />
        </label>
        <div className="flex gap-2">
          <label className="block w-1/2">
            <span className="text-gray-700">First Name</span>
            <input
              type="text"
              name="first_name"
              value={form.first_name}
              onChange={handleChange}
              className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
              required
            />
          </label>
          <label className="block w-1/2">
            <span className="text-gray-700">Last Name</span>
            <input
              type="text"
              name="last_name"
              value={form.last_name}
              onChange={handleChange}
              className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
              required
            />
          </label>
        </div>
        <label className="block">
          <span className="text-gray-700">Phone Number</span>
          <input
            type="text"
            name="phone_number"
            value={form.phone_number}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
            required
          />
        </label>
        <label className="block">
          <span className="text-gray-700">User Type</span>
          <select
            name="user_type"
            value={form.user_type}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
          >
            <option value="tenant">Tenant</option>
            <option value="owner">Owner</option>
            <option value="both">Both</option>
          </select>
        </label>
        <label className="block">
          <span className="text-gray-700">Date of Birth</span>
          <input
            type="date"
            name="date_of_birth"
            value={form.date_of_birth}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
            required
          />
        </label>
        <label className="block">
          <span className="text-gray-700">Gender</span>
          <select
            name="gender"
            value={form.gender}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </label>
        <label className="block">
          <span className="text-gray-700">Occupation</span>
          <input
            type="text"
            name="occupation"
            value={form.occupation}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
            required
          />
        </label>
        <label className="block">
          <span className="text-gray-700">Password</span>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
            required
          />
        </label>
        <label className="block">
          <span className="text-gray-700">Confirm Password</span>
          <input
            type="password"
            name="password_confirm"
            value={form.password_confirm}
            onChange={handleChange}
            className="mt-1 block w-full rounded border-gray-300 focus:ring-2 focus:ring-blue-400 p-2"
            required
          />
        </label>
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition disabled:opacity-60"
          disabled={loading}
        >
          {loading ? 'Registering...' : 'Register'}
        </button>
        <div className="text-center text-sm text-gray-500 mt-2">
          Already have an account?{' '}
          <a
            href="/login"
            className="text-blue-600 hover:underline"
          >
            Login
          </a>
        </div>
      </form>
    </div>
  );
}
