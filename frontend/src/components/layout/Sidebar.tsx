import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Bell,
  CheckSquare,
  ChevronLeft,
  ChevronRight,
  FileText,
  FolderTree,
  GitPullRequest,
  Grid,
  Layers,
  LayoutDashboard,
  Settings,
  Users,
} from 'lucide-react';
import styles from './Sidebar.module.css';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const mainNavItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/clients', label: 'Clients', icon: Users },
    { to: '/documents', label: 'Documents', icon: FileText },
    { to: '/workflows', label: 'Workflows', icon: GitPullRequest },
    { to: '/reminders', label: 'Reminders', icon: Bell },
    { to: '/reports', label: 'Reports', icon: Grid },
  ];

  const settingsNavItems = [
    { to: '/rules', label: 'Rules & Checklists', icon: CheckSquare },
    { to: '/doc-types', label: 'Document Types', icon: Layers },
    { to: '/users', label: 'Users', icon: Users },
    { to: '/integrations', label: 'Integrations', icon: FolderTree },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      <div className={styles.header}>
        {!collapsed && (
          <div className={styles.brand}>
            <div className={styles.logoIcon}>
              <Layers size={18} />
            </div>
            <span className={styles.brandName}>AI Docs Orchestrator</span>
          </div>
        )}
        <button
          className={styles.toggleBtn}
          onClick={onToggle}
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <div className={styles.navSection}>
        <div className={styles.group}>
          {!collapsed && <span className={styles.groupLabel}>MAIN</span>}
          {mainNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `${styles.navItem} ${isActive ? styles.active : ''}`
                }
                title={collapsed ? item.label : undefined}
              >
                <Icon className={styles.icon} />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </div>

        <div className={styles.group}>
          {!collapsed && <span className={styles.groupLabel}>SETTINGS</span>}
          {settingsNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `${styles.navItem} ${isActive ? styles.active : ''}`
                }
                title={collapsed ? item.label : undefined}
              >
                <Icon className={styles.icon} />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </div>
      </div>

      <div className={styles.footer}>
        <div className={styles.userAvatar}>OM</div>
        {!collapsed && (
          <div className={styles.userInfo}>
            <span className={styles.userName}>Omkar Mahindrakar</span>
            <span className={styles.userRole}>Administrator</span>
          </div>
        )}
      </div>
    </aside>
  );
};
