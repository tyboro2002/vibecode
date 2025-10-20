// Authentication Service for Zeus OAuth
// Place this file in: frontend/src/services/auth.ts

const API_BASE_URL = 'http://localhost:8000/api';

export interface User {
  username: string;
  name?: string;
  email?: string;
  [key: string]: any;
}

export interface AuthResponse {
  success: boolean;
  authenticated: boolean;
  user?: User;
  error?: string;
}

class AuthService {
  private authCache: AuthResponse | null = null;
  private cacheTimestamp: number = 0;
  private cacheDuration: number = 5000; // Cache for 5 seconds

  /**
   * Check if the user is currently authenticated (with caching)
   */
  async checkAuth(forceRefresh: boolean = false): Promise<AuthResponse> {
    // Return cached result if available and fresh
    const now = Date.now();
    if (!forceRefresh && this.authCache && (now - this.cacheTimestamp) < this.cacheDuration) {
      return this.authCache;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/check`, {
        credentials: 'include', // Important: Include cookies
      });
      const data = await response.json();
      
      // Cache the result
      this.authCache = data;
      this.cacheTimestamp = now;
      
      return data;
    } catch (error) {
      console.error('Auth check failed:', error);
      return { success: false, authenticated: false };
    }
  }

  /**
   * Clear the auth cache
   */
  clearCache(): void {
    this.authCache = null;
    this.cacheTimestamp = 0;
  }

  /**
   * Initiate the login flow by redirecting to Zeus
   */
  login(): void {
    // Store current location to return after login
    sessionStorage.setItem('loginReturnUrl', window.location.pathname);
    window.location.href = `${API_BASE_URL}/auth/login`;
  }

  /**
   * Logout the current user
   */
  async logout(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      const data = await response.json();
      
      // Clear cache on logout
      this.clearCache();
      
      return data.success;
    } catch (error) {
      console.error('Logout failed:', error);
      return false;
    }
  }

  /**
   * Get the current user's profile
   */
  async getProfile(): Promise<User | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/profile`, {
        credentials: 'include',
      });
      const data = await response.json();
      return data.authenticated ? data.user : null;
    } catch (error) {
      console.error('Failed to get profile:', error);
      return null;
    }
  }

  /**
   * Make an authenticated API request
   */
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const defaultOptions: RequestInit = {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    // If unauthorized, redirect to login
    if (response.status === 401) {
      this.login();
      throw new Error('Unauthorized - redirecting to login');
    }

    return response;
  }
}

export const authService = new AuthService();
export default authService;
