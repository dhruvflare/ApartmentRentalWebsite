// src/types/index.d.ts

export interface Property {
  id: number;
  title: string;
  price: number;
  image_url?: string;
  description?: string;
  // Add other fields returned by your API
}

export interface Review {
  id: number;
  rating: number;
  review_text: string;
  reviewer: { username: string };
  // Add any other fields
}

// Filter values can be string, number, boolean, or array of those
export type FilterValue = string | number | boolean | (string | number | boolean)[];

// Extend Filters here as needed with optional keys and 'FilterValue' types
export interface Filters {
  city?: string;
  bedrooms?: number;
  bathrooms?: number;
  price_min?: number;
  price_max?: number;
  [key: string]: FilterValue | undefined;  // flexible for additional filter params
}

// Response from properties list API endpoint
export interface PropertyListResponse {
  results: Property[];
  count: number;
  next?: string;
  previous?: string;
}
