'use client';

import { ChangeEvent } from 'react';
import { Filters } from '@/types';

interface FiltersSidebarProps {
  onChange: (filters: Filters) => void;
}

export default function FiltersSidebar({ onChange }: FiltersSidebarProps) {
  const handleCity = (e: ChangeEvent<HTMLInputElement>) => {
    onChange({ city: e.target.value });
  };

  return (
    <aside className="w-full max-w-xs bg-white rounded-xl shadow p-6 mb-6 md:mb-0 md:mr-8">
      <h3 className="font-semibold text-lg mb-4 text-blue-700">Filters</h3>
      <label className="block mb-4">
        <span className="block text-gray-700 mb-1">City</span>
        <input
          type="text"
          onChange={handleCity}
          className="block w-full mt-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-400 focus:outline-none transition"
          placeholder="Enter city name"
        />
      </label>
      {/* Add more filters here as needed */}
    </aside>
  );
}
