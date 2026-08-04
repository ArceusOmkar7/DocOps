import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { DashboardPage } from './pages/DashboardPage';
import { ClientsPage } from './pages/ClientsPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { WorkflowsPage } from './pages/WorkflowsPage';
import { SettingsPage } from './pages/SettingsPage';
import { NotFoundPage } from './pages/NotFoundPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="clients" element={<ClientsPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="workflows" element={<WorkflowsPage />} />
        <Route path="reminders" element={<DashboardPage />} />
        <Route path="reports" element={<DashboardPage />} />
        <Route path="rules" element={<SettingsPage />} />
        <Route path="doc-types" element={<SettingsPage />} />
        <Route path="users" element={<SettingsPage />} />
        <Route path="integrations" element={<SettingsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};
