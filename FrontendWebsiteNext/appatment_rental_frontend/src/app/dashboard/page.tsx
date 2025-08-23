import Link from 'next/link';
import { useContext } from 'react';
import { AuthContext } from '@/components/AuthContext';

export default function DashboardPage() {
  const { user } = useContext(AuthContext);

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-xl shadow p-8 mt-8 text-center">
      <h1 className="text-3xl font-bold text-blue-700 mb-4">Welcome to the Dashboard</h1>
      <p className="text-gray-600 mb-6">
        This dashboard is public. You can browse here without logging in.<br />
        To access your account features, please log in.
      </p>
      {user ? (
        <div className="text-green-600 font-semibold mb-4">You are logged in as {user.username}.</div>
      ) : (
        <Link href="/login" className="inline-block px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition font-semibold">Login</Link>
      )}
    </div>
  );
}
