import React, { createContext, useContext, useState, useCallback } from 'react';

interface DrawerContextValue {
  isOpen: boolean;
  activeDocumentId: string | null;
  activeResultId: string | null;
  openDrawer: (documentId?: string, resultId?: string) => void;
  closeDrawer: () => void;
}

const DrawerContext = createContext<DrawerContextValue>({
  isOpen: false,
  activeDocumentId: null,
  activeResultId: null,
  openDrawer: () => {},
  closeDrawer: () => {},
});

export const useDrawer = () => useContext(DrawerContext);

export const DrawerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);
  const [activeResultId, setActiveResultId] = useState<string | null>(null);

  const openDrawer = useCallback((documentId?: string, resultId?: string) => {
    if (documentId) setActiveDocumentId(documentId);
    if (resultId) setActiveResultId(resultId);
    setIsOpen(true);
  }, []);

  const closeDrawer = useCallback(() => {
    setIsOpen(false);
  }, []);

  return (
    <DrawerContext.Provider
      value={{
        isOpen,
        activeDocumentId,
        activeResultId,
        openDrawer,
        closeDrawer,
      }}
    >
      {children}
    </DrawerContext.Provider>
  );
};
