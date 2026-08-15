import api from './api';
import type { User } from '../types';

export interface LoginResponse {
  status: string;
  token?: string | null;
  user?: User;
  access_token?: string | null;
  message?: string;
}

export const authService = {
  // Login calls the backend /auth/login endpoint and uses the token/user it
  // returns. The frontend does not fabricate a token or user.
  login: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    const { data } = await api.post<LoginResponse>('/auth/login', { email, password });
    const token = data.token ?? data.access_token ?? '';
    const user: User =
      data.user ?? {
        id: 0,
        username: email,
        email,
        role: 'manager',
        isActive: true,
        createdAt: new Date().toISOString(),
      };
    if (!token) {
      throw new Error('Backend did not return an auth token');
    }
    return { token, user };
  },
};
