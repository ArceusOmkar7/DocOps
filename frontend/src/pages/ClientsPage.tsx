import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import { ErrorState } from '../components/common/ErrorState';
import { PageHeader } from '../components/common/PageHeader';
import { StatusBadge } from '../components/common/StatusBadge';
import { useClients, useCreateClient } from '../hooks/useClients';
import { useOrganizations } from '../hooks/useOrganizations';
import { clientStatusLabel } from '../lib/format';
import { ClientStatus } from '../types/api';
import ui from '../styles/ui.module.css';

const EMPTY_FORM = { name: '', tax_id: '', contact_person: '', email: '', phone: '' };

export const ClientsPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: clients = [], isLoading, isError } = useClients();
  const { data: orgs = [] } = useOrganizations();
  const createClient = useCreateClient();

  const dialogRef = useRef<HTMLDialogElement>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState('');
  const [query, setQuery] = useState('');

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    const reset = () => {
      setForm(EMPTY_FORM);
      setFormError('');
    };
    dialog.addEventListener('close', reset);
    return () => dialog.removeEventListener('close', reset);
  }, []);

  const q = query.trim().toLowerCase();
  const visible = clients.filter(
    (c) => !q || c.name.toLowerCase().includes(q) || (c.tax_id ?? '').toLowerCase().includes(q)
  );

  const update = (field: keyof typeof EMPTY_FORM) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [field]: e.target.value });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const orgId = orgs[0]?.id;
    if (!orgId) {
      setFormError('No firm record was found. Check that the backend is running and seeded.');
      return;
    }
    try {
      await createClient.mutateAsync({
        organization_id: orgId,
        name: form.name.trim(),
        tax_id: form.tax_id.trim() || undefined,
        contact_person: form.contact_person.trim() || undefined,
        email: form.email.trim() || undefined,
        phone: form.phone.trim() || undefined,
        status: ClientStatus.ON_TRACK,
      });
      dialogRef.current?.close();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'The client could not be saved.');
    }
  };

  return (
    <div className={ui.page}>
      <PageHeader
        title="Clients"
        actions={
          <button className={ui.btnPrimary} onClick={() => dialogRef.current?.showModal()}>
            <Plus size={15} strokeWidth={1.75} aria-hidden="true" />
            Add client
          </button>
        }
      />

      <section className={ui.panel} aria-label="Client directory">
        <div className={ui.panelHead}>
          <h2 className={ui.panelTitle}>
            All clients
            <span className={ui.panelCount}>{clients.length}</span>
          </h2>
          <label className={ui.search}>
            <Search size={14} className={ui.searchIcon} aria-hidden="true" />
            <input
              type="search"
              className={ui.input}
              placeholder="Search by name or GSTIN"
              aria-label="Search clients by name or GSTIN"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </label>
        </div>

        {isError ? (
          <ErrorState what="clients" />
        ) : isLoading ? (
          <div className={ui.empty} aria-busy="true">
            <div className={ui.skeletonRow} style={{ width: '60%' }} />
          </div>
        ) : visible.length === 0 ? (
          <div className={ui.empty}>
            <span className={ui.emptyTitle}>
              {clients.length === 0 ? 'No clients yet' : 'No clients match'}
            </span>
            <span className={ui.emptyText}>
              {clients.length === 0
                ? 'Use Add client to register the first one.'
                : 'Try a different name or GSTIN.'}
            </span>
          </div>
        ) : (
          <div className={ui.tableWrap}>
            <table className={ui.table}>
              <thead>
                <tr>
                  <th scope="col">Client</th>
                  <th scope="col">Contact</th>
                  <th scope="col">Phone</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((client) => (
                  <tr
                    key={client.id}
                    className={ui.rowLink}
                    onClick={() => navigate(`/documents?client=${client.id}`)}
                  >
                    <td>
                      <Link
                        to={`/documents?client=${client.id}`}
                        className={ui.primaryCell}
                        onClick={(e) => e.stopPropagation()}
                      >
                        {client.name}
                      </Link>
                      <span className={`${ui.sub} ${ui.id}`}>
                        {client.tax_id || 'No GSTIN on file'}
                      </span>
                    </td>
                    <td>
                      {client.contact_person || <span className={ui.muted}>Not recorded</span>}
                      {client.email && <span className={ui.sub}>{client.email}</span>}
                    </td>
                    <td style={{ whiteSpace: 'nowrap' }}>
                      {client.phone || <span className={ui.muted}>Not recorded</span>}
                    </td>
                    <td>
                      <StatusBadge
                        status={client.status}
                        label={clientStatusLabel(client.status)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <dialog ref={dialogRef} className={ui.dialog} aria-labelledby="add-client-title">
        <form onSubmit={handleCreate}>
          <div className={ui.dialogHead}>
            <h2 id="add-client-title" className={ui.panelTitle}>
              Add client
            </h2>
          </div>
          <div className={ui.dialogBody}>
            <div className={ui.field}>
              <label className={ui.label} htmlFor="client-name">
                Client or business name
              </label>
              <input
                id="client-name"
                className={ui.input}
                required
                placeholder="Rajput Steelworks Pvt Ltd"
                value={form.name}
                onChange={update('name')}
              />
            </div>
            <div className={ui.field}>
              <label className={ui.label} htmlFor="client-gstin">
                GSTIN
              </label>
              <input
                id="client-gstin"
                className={ui.input}
                placeholder="24AABCR5678Q1ZP"
                value={form.tax_id}
                onChange={update('tax_id')}
              />
            </div>
            <div className={ui.formRow}>
              <div className={ui.field}>
                <label className={ui.label} htmlFor="client-contact">
                  Contact person
                </label>
                <input
                  id="client-contact"
                  className={ui.input}
                  value={form.contact_person}
                  onChange={update('contact_person')}
                />
              </div>
              <div className={ui.field}>
                <label className={ui.label} htmlFor="client-phone">
                  Phone
                </label>
                <input
                  id="client-phone"
                  className={ui.input}
                  type="tel"
                  placeholder="+91 98240 11223"
                  value={form.phone}
                  onChange={update('phone')}
                />
              </div>
            </div>
            <div className={ui.field}>
              <label className={ui.label} htmlFor="client-email">
                Email
              </label>
              <input
                id="client-email"
                className={ui.input}
                type="email"
                value={form.email}
                onChange={update('email')}
              />
            </div>
            {formError && (
              <p className={ui.errorText} role="alert">
                {formError}
              </p>
            )}
          </div>
          <div className={ui.dialogFoot}>
            <button type="button" className={ui.btn} onClick={() => dialogRef.current?.close()}>
              Cancel
            </button>
            <button type="submit" className={ui.btnPrimary} disabled={createClient.isPending}>
              {createClient.isPending ? 'Saving' : 'Save client'}
            </button>
          </div>
        </form>
      </dialog>
    </div>
  );
};
