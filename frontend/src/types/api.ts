/**
 * Global TypeScript types for the application.
 */

// ---- User & Auth ----
export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: TokenResponse;
}

// ---- Business Profile ----
export interface BusinessProfile {
  id: string;
  user_id: string;
  business_name: string | null;
  manufacturer_name: string | null;
  manufacturer_address: string | null;
  manufacturer_city: string | null;
  manufacturer_state: string | null;
  manufacturer_pincode: string | null;
  country_of_origin: string | null;
  importer_name: string | null;
  importer_address: string | null;
  packer_name: string | null;
  packer_address: string | null;
  gstin: string | null;
  business_email: string | null;
  business_phone: string | null;
  warehouse_address: string | null;
  return_address: string | null;
  auto_fill_config: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

// ---- Product ----
export interface ProductImage {
  id: string;
  url: string;
  filename: string;
  image_type: string;
  sort_order: number;
  is_primary: boolean;
  is_ai_generated: boolean;
  created_at: string;
}

export interface Product {
  id: string;
  user_id: string;
  sku: string;
  product_name: string;
  brand: string | null;
  category_id: string | null;
  subcategory: string | null;
  product_type: string | null;
  description: string | null;
  short_description: string | null;
  bullet_points: string[] | null;
  price: number | null;
  mrp: number | null;
  cost_price: number | null;
  stock: number;
  color: string | null;
  size: string | null;
  material: string | null;
  weight: number | null;
  dimensions: { length?: number; width?: number; height?: number; unit?: string } | null;
  country_of_origin: string | null;
  manufacturer: string | null;
  manufacturer_address: string | null;
  packer: string | null;
  importer: string | null;
  keywords: string[] | null;
  search_terms: string[] | null;
  tags: string[] | null;
  status: 'draft' | 'active' | 'archived';
  images: ProductImage[];
  listing_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ---- Marketplace Listings ----
export interface MarketplaceListing {
  id: string;
  product_id: string;
  user_id: string;
  marketplace: 'amazon' | 'flipkart' | 'meesho';
  marketplace_listing_id: string | null;
  status: 'draft' | 'ai_generated' | 'validated' | 'needs_review' | 'approved' | 'publishing' | 'published' | 'error';
  listing_data: Record<string, unknown> | null;
  marketplace_specific_data: Record<string, unknown> | null;
  completion_percentage: number | null;
  validation_results: {
    is_valid: boolean;
    errors: { field: string; message: string }[];
    warnings: { field: string; message: string }[];
  } | null;
  version: number;
  error_message: string | null;
  published_at: string | null;
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ListingListResponse {
  items: MarketplaceListing[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ---- Marketplace Accounts ----
export interface MarketplaceAccount {
  id: string;
  user_id: string;
  marketplace: 'amazon' | 'flipkart' | 'meesho';
  account_id: string | null;
  account_name: string | null;
  status: 'connected' | 'disconnected' | 'error';
  config: Record<string, unknown> | null;
  last_sync_at: string | null;
  last_error: string | null;
  listing_count: number;
  created_at: string;
  updated_at: string;
}

// ---- Seller Memory ----
export interface SellerMemory {
  id: string;
  user_id: string;
  field_name: string;
  field_value: string;
  source: 'manual' | 'ai_suggested' | 'imported';
  scope: 'global' | 'marketplace' | 'product';
  marketplace: string | null;
  product_id: string | null;
  priority: number;
  is_active: boolean;
  usage_count: number;
  last_used_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SellerMemoryListResponse {
  items: SellerMemory[];
  total: number;
  page: number;
  page_size: number;
}

// ---- Dashboard ----
export interface DashboardStats {
  total_products: number;
  active_listings: number;
  draft_listings: number;
  needs_review_listings: number;
  publishing_errors: number;
  low_stock_products: number;
}

export interface MarketplaceBreakdown {
  marketplace: string;
  products: number;
  listings: number;
  errors: number;
  published: number;
}

export interface RecentActivity {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  message: string;
  created_at: string;
}

export interface DashboardData {
  stats: DashboardStats;
  marketplace_breakdown: MarketplaceBreakdown[];
  recent_activity: RecentActivity[];
}

// ---- Notifications ----
export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  category: string;
  title: string;
  message: string;
  data: Record<string, unknown> | null;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

// ---- Common ----
export interface SuccessResponse {
  success: boolean;
  message: string;
  data?: Record<string, unknown> | null;
}
