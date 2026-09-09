import React, { useState } from 'react';
import { Loader2, Plus, Users, X } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { useClients, useCreateClient } from '../hooks/useClients';
import { useOrganizations } from '../hooks/useOrganizations';
import { ClientStatus } from '../types/api';
import styles from './DashboardPage.module.css';

export const ClientsPage: React.FC = () => {
  const { data: clients = [], isLoading } = useClients();
  const { data: orgs = [] } = useOrganizations();
  const createClientMutation = useCreateClient();

  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    tax_id: '',
    contact_person: '',
    email: '',
    phone: '',
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name) return;

    // Use first available org ID or default fallback
    const orgId = orgs[0]?.id;
    if (!orgId) {
      alert('No organization found. Please ensure backend is running.');
      return;
    }

    try {
      await createClientMutation.mutateAsync({
        organization_id: orgId,
        name: formData.name,
        tax_id: formData.tax_id || undefined,
        contact_person: formData.contact_person || undefined,
        email: formData.email || undefined,
        phone: formData.phone || undefined,
        status: ClientStatus.ON_TRACK,
      });

      setShowModal(false);
      setFormData({ name: '', tax_id: '', contact_person: '', email: '', phone: '' });
    } catch (err: any) {
      alert(`Failed to create client: ${err.message}`);
    }
  };

  return (
    <div className={styles.container}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
            Client Management
          </h2>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            View and manage organizational clients and their compliance state.
          </p>
        </div>
        <button className={styles.btnPrimary} onClick={() => setShowModal(true)}>
          <Plus size={16} />
          Add Client
        </button>
      </div>

      <div className={styles.cardSection}>
        <div className={styles.tableContainer}>
          {isLoading ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
              <Loader2 size={24} className="animate-spin" style={{ margin: '0 auto 8px' }} />
              <span>Fetching clients...</span>
            </div>
          ) : clients.length === 0 ? (
            <div style={{ padding: 48, textAlign: 'center', color: '#64748b' }}>
              <Users size={36} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
              <div style={{ fontSize: 16, fontWeight: 600, color: '#0f172a' }}>
                No Clients Found
              </div>
              <div style={{ fontSize: 13, marginTop: 4 }}>
                Click "Add Client" above to register your first organizational client.
              </div>
            </div>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Client</th>
                  <th>Status</th>
                  <th>Tax ID (GSTIN)</th>
                  <th>Contact Person</th>
                  <th>Phone</th>
                  <th>Email</th>
                </tr>
              </thead>
              <tbody>
                {clients.map((client) => {
                  const initials = client.name
                    .split(' ')
                    .map((n) => n[0])
                    .join('')
                    .substring(0, 2)
                    .toUpperCase();

                  return (
                    <tr key={client.id}>
                      <td>
                        <div className={styles.clientCell}>
                          <div className={styles.avatar}>{initials}</div>
                          <div className={styles.clientInfo}>
                            <span className={styles.clientName}>{client.name}</span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={client.status || 'on_track'} />
                      </td>
                      <td style={{ color: '#475569', fontWeight: 500 }}>
                        {client.tax_id || 'N/A'}
                      </td>
                      <td>{client.contact_person || 'N/A'}</td>
                      <td style={{ color: 'var(--text-muted)' }}>{client.phone || 'N/A'}</td>
                      <td style={{ color: 'var(--text-muted)' }}>{client.email || 'N/A'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Add Client Modal */}
      {showModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
          onClick={() => setShowModal(false)}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: 12,
              width: 440,
              maxWidth: '90%',
              padding: 24,
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>Add New Client</h3>
              <button
                onClick={() => setShowModal(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 4 }}>
                  Client / Business Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Tech Solutions"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: 6,
                    border: '1px solid #cbd5e1',
                    fontSize: 13,
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 4 }}>
                  Tax ID / GSTIN
                </label>
                <input
                  type="text"
                  placeholder="e.g. 27ABCDE1234F1Z5"
                  value={formData.tax_id}
                  onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: 6,
                    border: '1px solid #cbd5e1',
                    fontSize: 13,
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 4 }}>
                    Contact Person
                  </label>
                  <input
                    type="text"
                    placeholder="Full name"
                    value={formData.contact_person}
                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: 6,
                      border: '1px solid #cbd5e1',
                      fontSize: 13,
                    }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 4 }}>
                    Phone
                  </label>
                  <input
                    type="text"
                    placeholder="+91 98765 43210"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: 6,
                      border: '1px solid #cbd5e1',
                      fontSize: 13,
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 4 }}>
                  Email Address
                </label>
                <input
                  type="email"
                  placeholder="client@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: 6,
                    border: '1px solid #cbd5e1',
                    fontSize: 13,
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 8 }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className={styles.actionBtn}
                  style={{ padding: '7px 14px', fontSize: 12 }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createClientMutation.isPending}
                  className={styles.btnPrimary}
                >
                  {createClientMutation.isPending ? 'Registering...' : 'Register Client'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
