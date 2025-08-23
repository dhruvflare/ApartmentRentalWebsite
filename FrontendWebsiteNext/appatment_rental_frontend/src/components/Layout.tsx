'use client';

import { ReactNode } from 'react';
import Link from 'next/link';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white shadow sticky top-0 z-10">
        <nav className="container mx-auto flex items-center justify-between py-4 px-6">
          <div className="text-2xl font-bold text-blue-600 tracking-tight">
            ApartmentRental
          </div>
          <div className="space-x-4">
            <Link
              href="/"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Home
            </Link>
            <Link
              href="/dashboard"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Dashboard
            </Link>
            <Link
              href="/login"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Register
            </Link>
          </div>
        </nav>
      </header>
      <main className="flex-1 container mx-auto px-4 py-8">{children}</main>
      <footer className="bg-white border-t py-4 text-center text-gray-500 text-sm mt-8">
        &copy; {new Date().getFullYear()} ApartmentRental. All rights reserved.
      </footer>
    </div>
  );
}
