/**
 * API client with JWT authentication and error handling.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface ApiResponse<T = unknown> {
  data?: T;
  error?: boolean;
  message?: string;
  details?: Record<string, unknown>;
}

class ApiError extends Error {
  status: number;
  details: Record<string, unknown>;

  constructor(message: string, status: number, details: Record<string, unknown> = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

function getTokens() {
  if (typeof window === 'undefined') return { access: null, refresh: null };
  const access = localStorage.getItem('access_token');
  const refresh = localStorage.getItem('refresh_token');
  return { access, refresh };
}

function setTokens(access: string, refresh: string) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

async function refreshAccessToken(): Promise<string | null> {
  const { refresh } = getTokens();
  if (!refresh) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    });

    if (!response.ok) {
      clearTokens();
      return null;
    }

    const data = await response.json();
    setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const { access } = getTokens();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };

  if (access) {
    headers['Authorization'] = `Bearer ${access}`;
  }

  // Remove Content-Type for FormData (browser sets it with boundary)
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 — try token refresh
  if (response.status === 401 && retry) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      return apiRequest<T>(endpoint, options, false);
    }
    clearTokens();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new ApiError('Session expired. Please log in again.', 401);
  }

  if (!response.ok) {
    let errorData: { message?: string; details?: Record<string, unknown> } = {};
    try {
      errorData = await response.json();
    } catch {
      // Ignore JSON parse error
    }
    throw new ApiError(
      errorData.message || `Request failed with status ${response.status}`,
      response.status,
      errorData.details || {},
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// Convenience methods
export const api = {
  get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  put: <T>(endpoint: string, body?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'DELETE' }),

  upload: <T>(endpoint: string, formData: FormData) =>
    apiRequest<T>(endpoint, { method: 'POST', body: formData }),
};

export { ApiError, setTokens, clearTokens, getTokens };
export type { ApiResponse };
