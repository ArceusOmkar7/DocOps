import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { DocumentDrawer } from '../documents/DocumentDrawer';
import { DrawerProvider, useDrawer } from '../../contexts/DrawerContext';
import styles from './AppShell.module.css';

const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(() => window.innerWidth < 800);
  const { isOpen, closeDrawer, activeDocumentId, activeResultId } = useDrawer();

  return (
    <div className={styles.appContainer}>
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <main className={styles.content}>
        <Outlet />
      </main>

      {isOpen && (
        <div className={styles.drawerPanel}>
          <DocumentDrawer
            isOpen={isOpen}
            onClose={closeDrawer}
            documentId={activeDocumentId || undefined}
            resultId={activeResultId || undefined}
          />
        </div>
      )}
    </div>
  );
};

export const AppShell: React.FC = () => {
  return (
    <DrawerProvider>
      <AppLayout />
    </DrawerProvider>
  );
};
