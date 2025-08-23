'use client';

import { createContext, ReactNode, useEffect, useState } from 'react';
import api from '@/lib/api';

type User = { id: number; username: string; user_type: string };
export const AuthContext = createContext<{ user: User | null }>({ user: null });

export function AuthContextProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api.get('auth/profile/')
      .then(res => setUser(res.data))
      .catch((err) => {
        if (err.response && err.response.status === 401) {
          setUser(null); // Not logged in, but don't reload or redirect
        } else {
          // Optionally handle other errors
          setUser(null);
        }
      });
  }, []);

  return <AuthContext.Provider value={{ user }}>{children}</AuthContext.Provider>;
}
