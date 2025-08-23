'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Property } from '@/types';

export default function PropertyCard({ id, title, price, image_url, description }: Property) {
  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden flex flex-col">
      {image_url && (
        <div className="relative h-48 w-full">
          <Image
            src={image_url}
            alt={title}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 400px"
            priority
          />
        </div>
      )}
      <div className="p-4 flex-1 flex flex-col">
        <h2 className="text-xl font-semibold text-gray-800 mb-1 truncate">{title}</h2>
        <p className="text-blue-600 font-bold text-lg mb-2">9{price.toLocaleString('en-IN')}</p>
        {description && <p className="text-gray-500 text-sm mb-3 line-clamp-2">{description}</p>}
        <Link href={`/properties/${id}`}>
          <span className="inline-block mt-auto px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-center cursor-pointer">View details</span>
        </Link>
      </div>
    </div>
  );
}
