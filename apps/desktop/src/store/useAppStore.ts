import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface UIState {
  sidebarOpen: boolean;
  token: string | null;
  toggleSidebar: () => void;
  setToken: (token: string | null) => void;
}

export const useAppStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      token: null,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setToken: (token) => set({ token }),
    }),
    {
      name: 'cognisphere-ui-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
