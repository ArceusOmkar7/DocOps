import React from 'react';
import { Link } from 'react-router-dom';
import { PageHeader } from '../components/common/PageHeader';
import ui from '../styles/ui.module.css';

export const NotFoundPage: React.FC = () => (
  <div className={ui.page}>
    <PageHeader title="Page not found" note="There is nothing at this address." />
    <div>
      <Link to="/" className={ui.btnPrimary}>
        Back to the Desk
      </Link>
    </div>
  </div>
);
