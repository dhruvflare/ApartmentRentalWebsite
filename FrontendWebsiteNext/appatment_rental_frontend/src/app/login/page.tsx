'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { saveToken } from '@/lib/auth';

interface LoginForm {
  username: string;
  password: string;
}

interface LoginResponse {
  token: string;
}

export default function LoginPage() {
  const [form, setForm] = useState<LoginForm>({ username: '', password: '' });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.post<LoginResponse>('auth/login/', form);
      saveToken(res.data.token);
      router.push('/');
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  return (
    <div className="flex min-h-[70vh] items-center justify-center bg-gray-50">
      <form
        onSubmit={onSubmit}
        className="bg-white shadow-lg rounded-xl p-8 w-full max-w-md flex flex-col gap-4"
      >
        <h1 className="text-2xl font-bold text-blue-700 mb-2 text-center">
          Sign in to your account
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
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition disabled:opacity-60"
          disabled={loading}
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
        <div className="text-center text-sm text-gray-500 mt-2">
          Don&apos;t have an account?{' '}
          <a
            href="/register"
            className="text-blue-600 hover:underline"
          >
            Register
          </a>
        </div>
      </form>
    </div>
  );
}
