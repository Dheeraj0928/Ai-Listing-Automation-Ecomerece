'use client';

import { ReactNode } from 'react';
import { AuthProvider } from '@/hooks/use-auth';
import { ToastProvider } from '@/hooks/use-toast';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <ToastProvider>
        {children}
      </ToastProvider>
    </AuthProvider>
  );
}
