# AI Multi-Marketplace Seller Listing Automation Platform

## Architecture & Implementation Plan

---

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend — Next.js 15 + TypeScript"
        FE[Next.js App Router]
        FE --> Pages[Pages & Layouts]
        FE --> Features[Feature Modules]
        FE --> UILib[UI Component Library]
    end

    subgraph "Backend — FastAPI + Python"
        API[FastAPI REST API]
        API --> Auth[Auth Service]
        API --> Products[Product Service]
        API --> Listings[Listing Service]
        API --> Memory[Memory Service]
        API --> AI[AI Service]
        API --> MKT[Marketplace Service]
    end

    subgraph "AI Layer"
        AIP[AI Provider Abstraction]
        AIP --> GPT[OpenAI / GPT]
        AIP --> Gemini[Google Gemini]
        AIP --> Local[Local Models]
    end

    subgraph "Marketplace Adapters"
        MA[MarketplaceProvider Interface]
        MA --> AZ[Amazon Adapter]
        MA --> FK[Flipkart Adapter]
        MA --> MS[Meesho Adapter]
    end

    subgraph "Infrastructure"
        DB[(PostgreSQL)]
        Redis[(Redis)]
        Queue[Celery Workers]
        S3[File Storage]
    end

    FE <--> API
    API <--> DB
    API <--> Redis
    API --> Queue
    Queue --> AIP
    Queue --> MA
    API --> S3
```

---

## 2. Database Schema (ERD)

```mermaid
erDiagram
    users {
        uuid id PK
        varchar email UK
        varchar password_hash
        varchar full_name
        varchar phone
        varchar avatar_url
        boolean is_active
        boolean is_verified
        timestamp email_verified_at
        timestamp last_login_at
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    business_profiles {
        uuid id PK
        uuid user_id FK
        varchar business_name
        varchar manufacturer_name
        text manufacturer_address
        varchar manufacturer_city
        varchar manufacturer_state
        varchar manufacturer_pincode
        varchar country_of_origin
        varchar importer_name
        text importer_address
        varchar packer_name
        text packer_address
        varchar gstin
        varchar business_email
        varchar business_phone
        text warehouse_address
        text return_address
        jsonb auto_fill_config
        timestamp created_at
        timestamp updated_at
    }

    marketplace_accounts {
        uuid id PK
        uuid user_id FK
        varchar marketplace "amazon|flipkart|meesho"
        varchar account_id
        varchar account_name
        varchar status "connected|disconnected|error"
        text encrypted_credentials
        jsonb config
        timestamp last_sync_at
        varchar last_error
        integer listing_count
        timestamp created_at
        timestamp updated_at
    }

    products {
        uuid id PK
        uuid user_id FK
        varchar sku UK
        varchar product_name
        varchar brand
        uuid category_id FK
        varchar subcategory
        varchar product_type
        text description
        text short_description
        jsonb bullet_points
        decimal price
        decimal mrp
        decimal cost_price
        integer stock
        varchar color
        varchar size
        varchar material
        decimal weight
        jsonb dimensions
        varchar country_of_origin
        varchar manufacturer
        text manufacturer_address
        varchar packer
        varchar importer
        jsonb keywords
        jsonb search_terms
        jsonb tags
        varchar status "draft|active|archived"
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    product_images {
        uuid id PK
        uuid product_id FK
        varchar url
        varchar filename
        varchar image_type "main|white_bg|lifestyle|closeup|feature|size_spec"
        integer sort_order
        boolean is_primary
        boolean is_ai_generated
        varchar ai_generation_id
        jsonb metadata
        timestamp created_at
    }

    product_dna {
        uuid id PK
        uuid product_id FK
        jsonb shapes
        jsonb dominant_colors
        varchar material_appearance
        varchar detected_product_type
        jsonb visible_components
        jsonb approximate_dimensions
        jsonb packaging_characteristics
        jsonb visual_features
        text raw_analysis
        varchar ai_provider
        varchar ai_model
        float confidence_score
        timestamp analyzed_at
        timestamp created_at
        timestamp updated_at
    }

    seller_memory {
        uuid id PK
        uuid user_id FK
        varchar field_name
        text field_value
        varchar source "manual|ai_suggested|imported"
        varchar scope "global|marketplace|product"
        varchar marketplace "amazon|flipkart|meesho|null"
        uuid product_id FK
        integer priority
        boolean is_active
        integer usage_count
        timestamp last_used_at
        timestamp created_at
        timestamp updated_at
    }

    marketplace_listings {
        uuid id PK
        uuid product_id FK
        uuid user_id FK
        varchar marketplace "amazon|flipkart|meesho"
        varchar marketplace_listing_id
        varchar status "draft|ai_generated|validated|needs_review|approved|publishing|published|error"
        jsonb listing_data
        jsonb marketplace_specific_data
        decimal completion_percentage
        jsonb validation_results
        integer version
        varchar error_message
        timestamp published_at
        timestamp last_synced_at
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    listing_versions {
        uuid id PK
        uuid listing_id FK
        integer version_number
        jsonb snapshot
        jsonb changes
        varchar changed_by
        text change_reason
        timestamp created_at
    }

    listing_images {
        uuid id PK
        uuid listing_id FK
        uuid product_image_id FK
        varchar marketplace "amazon|flipkart|meesho"
        varchar image_role "main|secondary|lifestyle"
        integer sort_order
        timestamp created_at
    }

    categories {
        uuid id PK
        varchar name
        uuid parent_id FK
        varchar marketplace "internal|amazon|flipkart|meesho"
        varchar marketplace_category_id
        jsonb required_attributes
        jsonb optional_attributes
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    marketplace_field_mappings {
        uuid id PK
        varchar marketplace "amazon|flipkart|meesho"
        varchar internal_field
        varchar marketplace_field
        varchar field_type
        boolean is_required
        integer max_length
        jsonb validation_rules
        jsonb enum_values
        timestamp created_at
        timestamp updated_at
    }

    validation_rules {
        uuid id PK
        varchar marketplace "amazon|flipkart|meesho"
        varchar field_name
        varchar rule_type "required|max_length|min_length|regex|enum|range"
        jsonb rule_config
        varchar error_message
        varchar severity "error|warning|info"
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    ai_generations {
        uuid id PK
        uuid user_id FK
        uuid product_id FK
        varchar generation_type "title|description|bullets|attributes|image|full_listing"
        varchar ai_provider
        varchar ai_model
        jsonb input_data
        jsonb output_data
        varchar status "pending|processing|completed|failed"
        float confidence_score
        integer tokens_used
        float cost_estimate
        timestamp started_at
        timestamp completed_at
        timestamp created_at
    }

    publish_jobs {
        uuid id PK
        uuid listing_id FK
        uuid user_id FK
        varchar marketplace "amazon|flipkart|meesho"
        varchar status "queued|processing|completed|failed|cancelled"
        jsonb request_payload
        jsonb response_payload
        varchar error_message
        integer retry_count
        timestamp started_at
        timestamp completed_at
        timestamp created_at
    }

    audit_logs {
        uuid id PK
        uuid user_id FK
        varchar action
        varchar entity_type
        uuid entity_id
        jsonb old_value
        jsonb new_value
        varchar ip_address
        varchar user_agent
        timestamp created_at
    }

    notifications {
        uuid id PK
        uuid user_id FK
        varchar type "info|warning|error|success"
        varchar category "listing|product|marketplace|system|ai"
        varchar title
        text message
        jsonb data
        boolean is_read
        timestamp read_at
        timestamp created_at
    }

    users ||--o| business_profiles : has
    users ||--o{ marketplace_accounts : has
    users ||--o{ products : owns
    users ||--o{ seller_memory : has
    users ||--o{ marketplace_listings : owns
    users ||--o{ audit_logs : generates
    users ||--o{ notifications : receives
    products ||--o{ product_images : has
    products ||--o| product_dna : has
    products ||--o{ marketplace_listings : generates
    products ||--o{ ai_generations : has
    marketplace_listings ||--o{ listing_versions : tracks
    marketplace_listings ||--o{ listing_images : has
    marketplace_listings ||--o{ publish_jobs : triggers
```

---

## 3. Project Folder Structure

### Backend (FastAPI)

```
backend/
├── alembic/                          # Database migrations
│   ├── versions/
│   └── env.py
├── app/
│   ├── __init__.py
│   ├── main.py                       # FastAPI app entry, middleware, lifespan
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                 # Pydantic BaseSettings
│   │   ├── security.py               # JWT, password hashing, auth utils
│   │   ├── database.py               # Async SQLAlchemy engine & session
│   │   ├── exceptions.py             # Custom exception classes
│   │   ├── middleware.py             # CORS, rate limiting, logging
│   │   └── dependencies.py          # FastAPI dependency injection
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── business_profile.py
│   │   ├── product.py
│   │   ├── product_image.py
│   │   ├── product_dna.py
│   │   ├── marketplace_account.py
│   │   ├── marketplace_listing.py
│   │   ├── listing_version.py
│   │   ├── seller_memory.py
│   │   ├── category.py
│   │   ├── marketplace_field_mapping.py
│   │   ├── validation_rule.py
│   │   ├── ai_generation.py
│   │   ├── publish_job.py
│   │   ├── audit_log.py
│   │   └── notification.py
│   ├── schemas/                      # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── business_profile.py
│   │   ├── product.py
│   │   ├── product_image.py
│   │   ├── product_dna.py
│   │   ├── marketplace.py
│   │   ├── listing.py
│   │   ├── seller_memory.py
│   │   ├── ai.py
│   │   ├── notification.py
│   │   └── common.py                # Pagination, error response, etc.
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py            # Aggregates all v1 routes
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── business_profiles.py
│   │       ├── products.py
│   │       ├── product_images.py
│   │       ├── product_dna.py
│   │       ├── marketplace_accounts.py
│   │       ├── listings.py
│   │       ├── seller_memory.py
│   │       ├── ai.py
│   │       ├── categories.py
│   │       ├── notifications.py
│   │       ├── search.py
│   │       └── dashboard.py
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── business_profile_service.py
│   │   ├── product_service.py
│   │   ├── product_image_service.py
│   │   ├── product_dna_service.py
│   │   ├── listing_service.py
│   │   ├── listing_generator_service.py
│   │   ├── listing_validator_service.py
│   │   ├── seller_memory_service.py
│   │   ├── marketplace_service.py
│   │   ├── ai_service.py
│   │   ├── image_service.py
│   │   ├── search_service.py
│   │   ├── notification_service.py
│   │   ├── audit_service.py
│   │   └── dashboard_service.py
│   ├── repositories/                 # Database access layer
│   │   ├── __init__.py
│   │   ├── base.py                   # Generic CRUD repository
│   │   ├── user_repo.py
│   │   ├── business_profile_repo.py
│   │   ├── product_repo.py
│   │   ├── product_image_repo.py
│   │   ├── listing_repo.py
│   │   ├── seller_memory_repo.py
│   │   ├── marketplace_repo.py
│   │   ├── category_repo.py
│   │   ├── notification_repo.py
│   │   └── audit_repo.py
│   ├── marketplace/                  # Marketplace adapter layer
│   │   ├── __init__.py
│   │   ├── base.py                   # MarketplaceProvider ABC
│   │   ├── amazon/
│   │   │   ├── __init__.py
│   │   │   ├── adapter.py
│   │   │   ├── field_mapping.py
│   │   │   └── schema.py
│   │   ├── flipkart/
│   │   │   ├── __init__.py
│   │   │   ├── adapter.py
│   │   │   ├── field_mapping.py
│   │   │   └── schema.py
│   │   └── meesho/
│   │       ├── __init__.py
│   │       ├── adapter.py
│   │       ├── field_mapping.py
│   │       └── schema.py
│   ├── ai/                           # AI provider abstraction
│   │   ├── __init__.py
│   │   ├── base.py                   # AIProvider ABC
│   │   ├── openai_provider.py
│   │   ├── gemini_provider.py
│   │   └── mock_provider.py
│   └── workers/                      # Celery/background tasks
│       ├── __init__.py
│       ├── celery_app.py
│       ├── ai_tasks.py
│       ├── image_tasks.py
│       ├── publish_tasks.py
│       ├── import_tasks.py
│       └── sync_tasks.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_products.py
│   ├── test_listings.py
│   ├── test_business_profile.py
│   └── test_seller_memory.py
├── uploads/                          # Local file storage (dev)
├── .env.example
├── alembic.ini
├── pyproject.toml
├── Dockerfile
└── README.md
```

### Frontend (Next.js 15)

```
frontend/
├── public/
│   └── assets/
├── src/
│   ├── app/                          # App Router — routing only
│   │   ├── layout.tsx
│   │   ├── page.tsx                  # Landing/redirect
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   ├── signup/page.tsx
│   │   │   └── forgot-password/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx            # Sidebar + topbar layout
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── products/
│   │   │   │   ├── page.tsx          # Product list
│   │   │   │   ├── new/page.tsx      # Create product
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx      # Product detail
│   │   │   │       └── listing/page.tsx  # Listing editor
│   │   │   ├── listings/
│   │   │   │   ├── page.tsx          # Listing list
│   │   │   │   └── [id]/page.tsx     # Listing detail
│   │   │   ├── marketplaces/page.tsx
│   │   │   ├── settings/
│   │   │   │   ├── business/page.tsx
│   │   │   │   ├── memory/page.tsx
│   │   │   │   └── ai/page.tsx
│   │   │   └── activity/page.tsx
│   │   └── api/                      # Next.js API routes (BFF proxy)
│   ├── features/                     # Feature modules
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── types.ts
│   │   ├── dashboard/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── types.ts
│   │   ├── products/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── types.ts
│   │   ├── listings/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── types.ts
│   │   ├── marketplace/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── types.ts
│   │   ├── memory/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── types.ts
│   │   └── ai-assistant/
│   │       ├── components/
│   │       ├── hooks/
│   │       └── types.ts
│   ├── components/                   # Global reusable UI components
│   │   ├── ui/                       # Primitives: Button, Input, Modal, etc.
│   │   ├── layout/                   # Sidebar, Topbar, PageHeader
│   │   ├── data/                     # DataTable, StatCard, Charts
│   │   └── feedback/                 # Toast, AlertBanner, Skeleton
│   ├── lib/
│   │   ├── api-client.ts             # Axios/fetch wrapper with auth
│   │   ├── auth.ts                   # Token management
│   │   └── utils.ts
│   ├── hooks/                        # Global hooks
│   │   ├── use-auth.ts
│   │   ├── use-toast.ts
│   │   └── use-debounce.ts
│   ├── types/                        # Global TypeScript types
│   │   ├── api.ts
│   │   ├── product.ts
│   │   ├── listing.ts
│   │   └── marketplace.ts
│   └── styles/
│       └── globals.css
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── Dockerfile
└── README.md
```

### Root

```
Ai-Listing-Automation-Ecomerece/
├── backend/
├── frontend/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. API Route Specification

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new seller |
| POST | `/api/v1/auth/login` | Login, returns JWT access + refresh tokens |
| POST | `/api/v1/auth/logout` | Invalidate refresh token |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/forgot-password` | Send password reset email |
| POST | `/api/v1/auth/reset-password` | Reset password with token |
| GET | `/api/v1/auth/me` | Get current user profile |
| PUT | `/api/v1/auth/me` | Update current user profile |

### Business Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/business-profile` | Get seller's business profile |
| PUT | `/api/v1/business-profile` | Create or update business profile |
| PATCH | `/api/v1/business-profile/auto-fill` | Update auto-fill configuration |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products (paginated, filterable) |
| POST | `/api/v1/products` | Create a new product |
| GET | `/api/v1/products/{id}` | Get product detail |
| PUT | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Soft-delete product |
| POST | `/api/v1/products/bulk-import` | Bulk import from CSV/Excel |
| GET | `/api/v1/products/{id}/dna` | Get Product DNA |
| POST | `/api/v1/products/{id}/analyze` | Trigger AI analysis of product |

### Product Images

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products/{id}/images` | List product images |
| POST | `/api/v1/products/{id}/images` | Upload image(s) |
| PUT | `/api/v1/products/{id}/images/{imageId}` | Update image metadata (rename, reorder, role) |
| DELETE | `/api/v1/products/{id}/images/{imageId}` | Delete image |
| POST | `/api/v1/products/{id}/images/{imageId}/set-primary` | Set primary image |
| POST | `/api/v1/products/{id}/images/generate` | AI-generate catalog images |
| POST | `/api/v1/products/{id}/images/{imageId}/remove-bg` | Remove background |

### Marketplace Listings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/listings` | List all listings (filterable by marketplace, status) |
| POST | `/api/v1/listings/generate` | Generate listings for a product |
| GET | `/api/v1/listings/{id}` | Get listing detail |
| PUT | `/api/v1/listings/{id}` | Update listing data |
| POST | `/api/v1/listings/{id}/validate` | Validate listing against marketplace rules |
| POST | `/api/v1/listings/{id}/approve` | Approve listing for publishing |
| POST | `/api/v1/listings/{id}/publish` | Publish listing to marketplace |
| GET | `/api/v1/listings/{id}/versions` | Get version history |
| POST | `/api/v1/listings/{id}/rollback/{version}` | Rollback to a version |
| POST | `/api/v1/listings/bulk-validate` | Bulk validate listings |
| POST | `/api/v1/listings/bulk-publish` | Bulk publish listings |

### Seller Memory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/memory` | List all memorized values |
| POST | `/api/v1/memory` | Save a new memory entry |
| PUT | `/api/v1/memory/{id}` | Update memory entry |
| DELETE | `/api/v1/memory/{id}` | Deactivate memory entry |
| GET | `/api/v1/memory/resolve/{field}` | Resolve value by hierarchy (product → marketplace → global) |
| POST | `/api/v1/memory/propagate` | Propagate updated value to drafts |

### Marketplace Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/marketplaces` | List connected marketplaces |
| POST | `/api/v1/marketplaces` | Connect a new marketplace account |
| GET | `/api/v1/marketplaces/{marketplace}` | Get marketplace account details |
| PUT | `/api/v1/marketplaces/{marketplace}` | Update marketplace config |
| DELETE | `/api/v1/marketplaces/{marketplace}` | Disconnect marketplace |
| POST | `/api/v1/marketplaces/{marketplace}/sync` | Trigger manual sync |
| GET | `/api/v1/marketplaces/{marketplace}/categories` | Get marketplace categories |

### AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/generate-title` | Generate title for product |
| POST | `/api/v1/ai/generate-description` | Generate description |
| POST | `/api/v1/ai/generate-bullets` | Generate bullet points |
| POST | `/api/v1/ai/extract-attributes` | Extract attributes from text/image |
| POST | `/api/v1/ai/analyze-image` | Analyze product image for DNA |
| POST | `/api/v1/ai/generate-image` | Generate catalog image |
| POST | `/api/v1/ai/chat` | AI assistant chat endpoint |
| GET | `/api/v1/ai/generations` | List AI generation history |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/stats` | Dashboard statistics |
| GET | `/api/v1/dashboard/marketplace-breakdown` | Per-marketplace stats |
| GET | `/api/v1/dashboard/recent-activity` | Recent activity feed |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications` | List notifications (paginated) |
| PUT | `/api/v1/notifications/{id}/read` | Mark as read |
| PUT | `/api/v1/notifications/read-all` | Mark all as read |
| GET | `/api/v1/notifications/unread-count` | Get unread count |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search?q={query}` | Global search across products, listings, SKUs |

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/categories` | List internal categories |
| GET | `/api/v1/categories/{marketplace}` | List marketplace-specific categories |

---

## 5. Marketplace Adapter Architecture

```mermaid
classDiagram
    class MarketplaceProvider {
        <<abstract>>
        +marketplace_name: str
        +connect(credentials) ConnectionResult
        +disconnect() bool
        +validate_listing(listing) ValidationResult
        +create_listing(listing) PublishResult
        +update_listing(listing_id, data) PublishResult
        +get_listing(listing_id) ListingData
        +upload_image(listing_id, image) ImageResult
        +update_inventory(sku, quantity) SyncResult
        +update_price(sku, price) SyncResult
        +get_orders(filters) OrderList
        +get_inventory(filters) InventoryList
        +get_categories() CategoryList
        +get_attributes(category_id) AttributeList
        +get_field_mapping() FieldMapping
    }

    class AmazonAdapter {
        -api_client: AmazonSPAPIClient
        +marketplace_name = "amazon"
    }

    class FlipkartAdapter {
        -api_client: FlipkartAPIClient
        +marketplace_name = "flipkart"
    }

    class MeeshoAdapter {
        -api_client: MeeshoAPIClient
        +marketplace_name = "meesho"
    }

    class MockAdapter {
        +marketplace_name: str
        -mock_data: dict
        +Note: "Used during development"
    }

    MarketplaceProvider <|-- AmazonAdapter
    MarketplaceProvider <|-- FlipkartAdapter
    MarketplaceProvider <|-- MeeshoAdapter
    MarketplaceProvider <|-- MockAdapter

    class MarketplaceFactory {
        +get_adapter(marketplace: str) MarketplaceProvider
        +register_adapter(name, adapter_class)
    }

    MarketplaceFactory --> MarketplaceProvider : creates
```

### Field Mapping Flow

```mermaid
flowchart LR
    subgraph "Internal Product Master"
        PM[manufacturer_address]
    end

    subgraph "Marketplace Mappings"
        AM["Amazon: manufacturer_address"]
        FM["Flipkart: manufacturer_details"]
        MM["Meesho: manufacturer_address"]
    end

    subgraph "Adapters Transform"
        AA[AmazonAdapter.transform]
        FA[FlipkartAdapter.transform]
        MA[MeeshoAdapter.transform]
    end

    PM --> AA --> AM
    PM --> FA --> FM
    PM --> MA --> MM
```

---

## 6. AI Provider Abstraction

```mermaid
classDiagram
    class AIProvider {
        <<abstract>>
        +provider_name: str
        +generate_title(product_data, marketplace) TitleResult
        +generate_description(product_data, marketplace) DescriptionResult
        +generate_bullets(product_data, marketplace) BulletsResult
        +extract_attributes(text_or_image) AttributeResult
        +analyze_product_image(image) ProductDNA
        +generate_catalog_image(product_dna, style) ImageResult
        +validate_listing(listing_data, rules) ValidationResult
        +chat(messages, context) ChatResponse
    }

    class OpenAIProvider {
        -client: OpenAI
        -text_model: str
        -vision_model: str
        -image_model: str
    }

    class GeminiProvider {
        -client: GoogleAI
        -text_model: str
        -vision_model: str
    }

    class MockAIProvider {
        +Note: "Returns realistic mock data for dev"
    }

    AIProvider <|-- OpenAIProvider
    AIProvider <|-- GeminiProvider
    AIProvider <|-- MockAIProvider
```

---

## 7. Seller Memory Hierarchy Resolution

```mermaid
flowchart TD
    Start["Resolve field value for<br/>Product X on Amazon"]
    
    Q1{"Product-specific value<br/>for this field?"}
    Q2{"Amazon-specific value<br/>for this field?"}
    Q3{"Global business default<br/>for this field?"}
    
    V1["Use Product-specific value"]
    V2["Use Amazon-specific value"]
    V3["Use Business default value"]
    V4["Field empty — needs input"]
    
    Start --> Q1
    Q1 -->|Yes| V1
    Q1 -->|No| Q2
    Q2 -->|Yes| V2
    Q2 -->|No| Q3
    Q3 -->|Yes| V3
    Q3 -->|No| V4
```

---

## 8. Listing Publishing Workflow

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> AI_Generated: AI generates listing
    AI_Generated --> Validated: Auto-validate
    Validated --> Needs_Review: Issues found
    Validated --> Approved: All checks pass
    Needs_Review --> Validated: Issues fixed
    Approved --> Publishing: Seller clicks Publish
    Publishing --> Published: Success
    Publishing --> Error: API failure
    Error --> Approved: Retry
    Published --> Draft: Edit published listing
```

---

## 9. Development Roadmap

### Phase 1 — Foundation (IMPLEMENTING NOW)

> [!IMPORTANT]
> This is the first deliverable. Everything below will be fully built and functional.

| Component | Details |
|-----------|---------|
| **Authentication** | Signup, login, logout, JWT access/refresh tokens, password hashing (bcrypt), protected routes, forgot password flow |
| **Business Profile** | Full CRUD with auto-fill config, all 16 business fields |
| **Product Master** | Full CRUD, search, filter, paginate. All 30+ product fields |
| **Dashboard** | Stats cards, marketplace breakdown, recent activity feed |
| **Database** | PostgreSQL with Alembic migrations for all Phase 1 tables |
| **Backend** | FastAPI with layered architecture, all Phase 1 API endpoints |
| **Frontend** | Next.js 15 with auth flow, dashboard, product management, business profile settings |
| **Docker** | docker-compose with PostgreSQL + Redis + backend + frontend |

### Phase 2 — AI Intelligence

| Component | Details |
|-----------|---------|
| Product images upload & management | |
| Product DNA analysis via AI vision | |
| AI text generation (title, description, bullets) | |
| AI attribute extraction | |

### Phase 3 — Seller Memory & Validation

| Component | Details |
|-----------|---------|
| Seller Memory CRUD & resolution hierarchy | |
| Auto-fill from memory | |
| Listing completeness checker | |
| Validation rules engine | |

### Phase 4 — Marketplace Schemas

| Component | Details |
|-----------|---------|
| Marketplace schema configuration | |
| Amazon adapter (MOCK) | |
| Flipkart adapter (MOCK) | |
| Meesho adapter (MOCK) | |
| Field mapping engine | |

### Phase 5 — Image Generation

| Component | Details |
|-----------|---------|
| AI catalog image generation | |
| Background removal | |
| Image manager (reorder, assign, crop) | |
| Marketplace-specific image assignment | |

### Phase 6 — Marketplace Integration

| Component | Details |
|-----------|---------|
| Real marketplace API clients (where available) | |
| Listing creation/update via API | |
| Inventory sync | |
| Price sync | |

### Phase 7 — Bulk Operations

| Component | Details |
|-----------|---------|
| CSV/Excel bulk import | |
| Bulk AI generation | |
| Bulk validation & approval | |
| Bulk publishing | |
| Background job queue (Celery) | |
| Notifications system | |

### Phase 8 — Advanced Features

| Component | Details |
|-----------|---------|
| Listing version history & rollback | |
| Smart change detection & propagation | |
| AI assistant chat | |
| Advanced analytics | |
| Audit logs viewer | |
| Global search | |

---

## 10. Proposed Changes — Phase 1 Implementation

### Backend

#### [NEW] `backend/app/main.py`
FastAPI application entry with CORS, lifespan, middleware, and router registration.

#### [NEW] `backend/app/core/config.py`
Pydantic BaseSettings for all environment variables (DB URL, JWT secret, Redis URL, AI keys).

#### [NEW] `backend/app/core/security.py`
Password hashing with bcrypt, JWT token creation/verification, OAuth2PasswordBearer dependency.

#### [NEW] `backend/app/core/database.py`
Async SQLAlchemy engine, sessionmaker, Base model with UUID PK mixin, get_db dependency.

#### [NEW] `backend/app/core/exceptions.py`
Custom exceptions: NotFoundError, UnauthorizedError, ValidationError, ConflictError. Exception handlers.

#### [NEW] `backend/app/models/*.py`
SQLAlchemy models for: User, BusinessProfile, Product, ProductImage, MarketplaceListing, Category, AuditLog, Notification.

#### [NEW] `backend/app/schemas/*.py`
Pydantic models for all request/response payloads with full validation.

#### [NEW] `backend/app/repositories/*.py`
Generic CRUD base + specific repos for user, product, business_profile, listing.

#### [NEW] `backend/app/services/*.py`
Auth service, product service, business profile service, dashboard service with full business logic.

#### [NEW] `backend/app/api/v1/*.py`
All Phase 1 route handlers: auth, products, business_profiles, dashboard.

#### [NEW] `backend/tests/`
Unit tests for auth, product CRUD, business profile CRUD.

---

### Frontend

#### [NEW] `frontend/src/app/(auth)/login/page.tsx`
Login page with email/password form, JWT token storage, redirect.

#### [NEW] `frontend/src/app/(auth)/signup/page.tsx`
Signup page with validation, error handling, auto-redirect to dashboard.

#### [NEW] `frontend/src/app/(dashboard)/layout.tsx`
Dashboard layout with sidebar navigation, topbar with user menu, notification bell.

#### [NEW] `frontend/src/app/(dashboard)/dashboard/page.tsx`
Dashboard with stat cards, marketplace breakdown, recent activity feed.

#### [NEW] `frontend/src/app/(dashboard)/products/page.tsx`
Product list with search, filter by status/category, pagination, bulk actions.

#### [NEW] `frontend/src/app/(dashboard)/products/new/page.tsx`
Product creation form with all 30+ fields, auto-fill from business profile.

#### [NEW] `frontend/src/app/(dashboard)/products/[id]/page.tsx`
Product detail view with edit capability, image section, listing status.

#### [NEW] `frontend/src/app/(dashboard)/settings/business/page.tsx`
Business profile form with all 16 fields, auto-fill toggle per field.

#### [NEW] `frontend/src/features/auth/`
Auth components, hooks (useAuth), services (login, signup, logout API calls).

#### [NEW] `frontend/src/components/ui/`
Button, Input, Select, Modal, Badge, StatCard, DataTable, Sidebar, Topbar.

---

### Infrastructure

#### [NEW] `docker-compose.yml`
PostgreSQL 16, Redis 7, backend (FastAPI/Uvicorn), frontend (Next.js dev).

#### [NEW] `.env.example`
All required environment variables documented.

#### [NEW] `README.md`
Setup instructions, architecture overview, development guide.

---

## Verification Plan

### Automated Tests
```bash
# Backend unit tests
cd backend && pytest tests/ -v

# Frontend type checking
cd frontend && npx tsc --noEmit

# Frontend lint
cd frontend && npm run lint
```

### Manual Verification
- Sign up a new user → Login → Verify JWT works
- Create business profile → Verify data persists
- Create product → Edit → Delete → Verify CRUD works
- Dashboard → Verify stats reflect actual data
- All API endpoints respond correctly via Swagger UI at `/docs`

---

## Open Questions

> [!IMPORTANT]
> **AI Provider**: Which AI provider should we use for Phase 2? Options: OpenAI (GPT-4o), Google Gemini, or both? This determines which API key to configure. For Phase 1, no AI integration is needed.

> [!IMPORTANT]
> **File Storage**: For product images, should we use local filesystem storage for now, or set up S3-compatible storage (MinIO in Docker) from the start?

> [!NOTE]
> **Email Service**: Forgot password flow needs an email service. For Phase 1, we can log the reset token to console and implement email (SendGrid/SES) later. Is this acceptable?
