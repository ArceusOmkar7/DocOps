import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { DocumentDrawer } from '../documents/DocumentDrawer';
import { DrawerProvider, useDrawer } from '../../contexts/DrawerContext';
import styles from './AppShell.module.css';

const ROUTE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Dashboard', subtitle: 'Overview of document operations' },
  '/clients': { title: 'Clients', subtitle: 'All clients and their document status' },
  '/documents': { title: 'Documents', subtitle: 'Document repository & extraction state' },
  '/workflows': { title: 'Workflows', subtitle: 'Active client compliance & filing workflows' },
  '/reminders': { title: 'Reminders', subtitle: 'Automated client follow-up notifications' },
  '/reports': { title: 'Reports', subtitle: 'Analytics and tax filing readiness summaries' },
  '/rules': { title: 'Rules & Checklists', subtitle: 'Validation rules and document requirements' },
  '/doc-types': { title: 'Document Types', subtitle: 'Supported schema configurations' },
  '/users': { title: 'Users & Permissions', subtitle: 'Manage organization team members' },
  '/integrations': { title: 'Integrations', subtitle: 'Connect Tally, GST Portal, & Cloud Storage' },
  '/settings': { title: 'Settings', subtitle: 'Organization settings and API keys' },
};

const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const { isOpen, closeDrawer } = useDrawer();

  const activeMeta = ROUTE_TITLES[location.pathname] || {
    title: 'AI Docs Orchestrator',
    subtitle: 'Autonomous document workflow platform',
  };

  return (
    <div className={styles.appContainer}>
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <div className={styles.mainWrapper}>
        <TopBar title={activeMeta.title} subtitle={activeMeta.subtitle} />
        <div className={styles.contentArea}>
          <main className={`${styles.content} ${isOpen ? styles.contentShifted : ''}`}>
            <Outlet />
          </main>
          {isOpen && (
            <div className={styles.drawerPanel}>
              <DocumentDrawer isOpen={isOpen} onClose={closeDrawer} />
            </div>
          )}
        </div>
      </div>
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
