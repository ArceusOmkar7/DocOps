import React from 'react';
import ui from '../../styles/ui.module.css';

export const ErrorState: React.FC<{ what: string }> = ({ what }) => (
  <div className={ui.empty} role="alert">
    <span className={ui.emptyTitle}>Could not load {what}</span>
    <span className={ui.emptyText}>
      Patra could not reach the server. Check that the backend is running on port 8000, then
      reload this page.
    </span>
  </div>
);
