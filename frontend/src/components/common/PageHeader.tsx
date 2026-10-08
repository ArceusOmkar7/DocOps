import React from 'react';
import styles from './PageHeader.module.css';

interface PageHeaderProps {
  title: string;
  /** One plain line under the title, only when it tells the reader something. */
  note?: React.ReactNode;
  actions?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title, note, actions }) => (
  <header className={styles.header}>
    <div className={styles.text}>
      <h1 className={styles.title}>{title}</h1>
      {note && <p className={styles.note}>{note}</p>}
    </div>
    {actions && <div className={styles.actions}>{actions}</div>}
  </header>
);
