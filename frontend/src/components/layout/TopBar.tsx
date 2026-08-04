import React from 'react';
import { Bell, Search } from 'lucide-react';
import styles from './TopBar.module.css';

interface TopBarProps {
  title?: string;
  subtitle?: string;
  onSearchChange?: (val: string) => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  title = 'Dashboard',
  subtitle = 'Overview of document operations',
  onSearchChange,
}) => {
  return (
    <header className={styles.topbar}>
      <div className={styles.titleSection}>
        <h1 className={styles.title}>{title}</h1>
        <span className={styles.subtitle}>{subtitle}</span>
      </div>

      <div className={styles.rightSection}>
        <div className={styles.searchBox}>
          <Search size={16} />
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Search clients, documents..."
            onChange={(e) => onSearchChange?.(e.target.value)}
          />
          <span className={styles.shortcut}>⌘ K</span>
        </div>

        <button className={styles.iconBtn} title="Notifications">
          <Bell size={18} />
          <span className={styles.badge}>3</span>
        </button>
      </div>
    </header>
  );
};
