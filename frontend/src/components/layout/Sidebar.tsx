import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ChevronsLeft,
  ChevronsRight,
  ClipboardList,
  FileText,
  ListChecks,
  Settings,
  Users,
} from 'lucide-react';
import { useDocuments } from '../../hooks/useDocuments';
import { useOrganizations } from '../../hooks/useOrganizations';
import { documentBucket } from '../../lib/readiness';
import styles from './Sidebar.module.css';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const NAV_ITEMS = [
  { to: '/', label: 'Desk', icon: ClipboardList, end: true },
  { to: '/clients', label: 'Clients', icon: Users },
  { to: '/documents', label: 'Documents', icon: FileText, showReviewCount: true },
  { to: '/workflows', label: 'Filings', icon: ListChecks },
];

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const { data: documents = [] } = useDocuments();
  const { data: organizations = [] } = useOrganizations();

  const reviewCount = documents.filter((d) => documentBucket(d) === 'review').length;
  const firmName = organizations[0]?.name;

  const renderLink = (item: (typeof NAV_ITEMS)[number] | { to: string; label: string; icon: typeof Settings }) => {
    const Icon = item.icon;
    const count = 'showReviewCount' in item && item.showReviewCount ? reviewCount : 0;
    return (
      <NavLink
        key={item.to}
        to={item.to}
        end={'end' in item ? item.end : false}
        className={({ isActive }) => `${styles.navItem} ${isActive ? styles.active : ''}`}
        title={collapsed ? item.label : undefined}
      >
        <Icon size={17} strokeWidth={1.75} className={styles.icon} aria-hidden="true" />
        {!collapsed && <span className={styles.navLabel}>{item.label}</span>}
        {count > 0 && (
          <span
            className={styles.count}
            aria-label={`${count} documents need review`}
            title={`${count} documents need review`}
          >
            {count}
          </span>
        )}
      </NavLink>
    );
  };

  return (
    <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      <div className={styles.header}>
        <div className={styles.brand}>
          <svg
            className={styles.mark}
            width="26"
            height="26"
            viewBox="0 0 32 32"
            fill="none"
            aria-hidden="true"
          >
            <path d="M8 7h5v18H8V7z" fill="#ffffff" />
            <path d="M13 7l6 0l-6 6z" fill="#3fc896" />
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M13 10h6.5a4.5 4.5 0 014.5 4.5v0a4.5 4.5 0 01-4.5 4.5H13V10zm4.5 3h-1.5v3h1.5a1.5 1.5 0 001.5-1.5v0a1.5 1.5 0 00-1.5-1.5z"
              fill="#ffffff"
            />
          </svg>
          {!collapsed && <span className={styles.brandName}>Patra</span>}
        </div>
      </div>

      <nav className={styles.nav} aria-label="Main">
        {NAV_ITEMS.map(renderLink)}
      </nav>

      <div className={styles.bottom}>
        {renderLink({ to: '/settings', label: 'Settings', icon: Settings })}

        {!collapsed && firmName && (
          <div className={styles.firm}>
            <span className={styles.firmLabel}>Firm</span>
            <span className={styles.firmName}>{firmName}</span>
          </div>
        )}

        <button
          className={styles.toggle}
          onClick={onToggle}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronsRight size={16} strokeWidth={1.75} />
          ) : (
            <>
              <ChevronsLeft size={16} strokeWidth={1.75} />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};
