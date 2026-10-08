import React from 'react';
import type {
  BankStatement,
  GSTReturn,
  Invoice,
  InvestmentProof,
  TDSForm,
} from '../../types/api';
import { formatInr, formatRupees } from '../../lib/format';
import styles from './DocumentDrawer.module.css';

const MISSING = 'Not found';

const orNA = (value?: string | number | null): string =>
  value == null || value === '' ? MISSING : String(value);

// ── Shared pieces ─────────────────────────────────────────────────────────

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className={styles.section}>
    <h3 className={styles.sectionTitle}>{title}</h3>
    {children}
  </section>
);

interface Entry {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}

const Fields: React.FC<{ entries: Entry[] }> = ({ entries }) => (
  <dl className={styles.fields}>
    {entries.map((entry) => {
      const missing = entry.value === MISSING;
      return (
        <div key={entry.label} className={styles.field}>
          <dt className={styles.fieldLabel}>{entry.label}</dt>
          <dd
            className={
              missing ? styles.fieldMissing : entry.mono ? styles.fieldMono : styles.fieldValue
            }
          >
            {entry.value}
          </dd>
        </div>
      );
    })}
  </dl>
);

interface TotalRow {
  label: string;
  value: string;
  strong?: boolean;
}

const Totals: React.FC<{ rows: TotalRow[] }> = ({ rows }) => (
  <dl className={styles.totals}>
    {rows.map((row) => (
      <div key={row.label} className={row.strong ? styles.totalStrong : styles.totalRow}>
        <dt>{row.label}</dt>
        <dd>{row.value}</dd>
      </div>
    ))}
  </dl>
);

const Table: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className={styles.tableWrapper}>
    <table className={styles.table}>{children}</table>
  </div>
);

// ── Invoice ───────────────────────────────────────────────────────────────

const Party: React.FC<{ role: string; party?: Invoice['seller'] }> = ({ role, party }) => (
  <div className={styles.party}>
    <span className={styles.fieldLabel}>{role}</span>
    <span className={styles.partyName}>{orNA(party?.name)}</span>
    {party?.tax_id && <span className={styles.fieldMono}>GSTIN {party.tax_id}</span>}
    {party?.address && (
      <span className={styles.partyMeta}>
        {typeof party.address === 'string'
          ? party.address
          : [party.address.line1, party.address.city, party.address.state]
              .filter(Boolean)
              .join(', ')}
      </span>
    )}
  </div>
);

export const InvoiceView: React.FC<{ data: Partial<Invoice> }> = ({ data }) => {
  const items = data.items ?? [];
  const tax = data.tax;
  const taxRows: TotalRow[] = tax
    ? ([
        ['CGST', tax.cgst],
        ['SGST', tax.sgst],
        ['IGST', tax.igst],
        ['VAT', tax.vat],
        [tax.other_tax_label || 'Other tax', tax.other_tax_amount],
      ] as [string, number | null | undefined][])
        .filter(([, amount]) => amount != null && amount !== 0)
        .map(([label, amount]) => ({ label, value: formatRupees(amount) }))
    : [];

  const totals: TotalRow[] = [
    { label: 'Subtotal', value: formatRupees(data.subtotal) },
    ...taxRows,
    ...(taxRows.length === 0 ? [{ label: 'Total tax', value: formatRupees(data.total_tax) }] : []),
    ...(data.amount_paid ? [{ label: 'Amount paid', value: formatRupees(data.amount_paid) }] : []),
    { label: 'Total', value: formatRupees(data.total), strong: true },
  ];

  return (
    <>
      <Section title="Invoice">
        <Fields
          entries={[
            { label: 'Invoice number', value: orNA(data.invoice_number), mono: true },
            { label: 'Invoice date', value: orNA(data.invoice_date) },
            { label: 'Due date', value: orNA(data.due_date) },
            { label: 'Currency', value: orNA(data.currency) },
          ]}
        />
      </Section>

      {(data.seller || data.buyer) && (
        <Section title="Parties">
          <div className={styles.parties}>
            <Party role="Seller" party={data.seller} />
            <Party role="Buyer" party={data.buyer} />
          </div>
        </Section>
      )}

      {items.length > 0 && (
        <Section title={`Line items (${items.length})`}>
          <Table>
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Description</th>
                <th scope="col" className={styles.num}>Qty</th>
                <th scope="col" className={styles.num}>Unit price</th>
                <th scope="col" className={styles.num}>Line total</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, idx) => (
                <tr key={idx}>
                  <td className={styles.muted}>{idx + 1}</td>
                  <td>{item.description || 'Item'}</td>
                  <td className={styles.num}>{item.quantity ?? 1}</td>
                  <td className={styles.num}>{formatRupees(item.unit_price)}</td>
                  <td className={styles.num}>{formatRupees(item.line_total)}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Section>
      )}

      <Section title="Totals">
        <Totals rows={totals} />
      </Section>
    </>
  );
};

// ── Bank statement ────────────────────────────────────────────────────────

export const BankStatementView: React.FC<{ data: Partial<BankStatement> }> = ({ data }) => {
  const txns = data.transactions ?? [];
  const debits = txns.reduce((sum, t) => sum + (t.debit ?? 0), 0);
  const credits = txns.reduce((sum, t) => sum + (t.credit ?? 0), 0);

  return (
    <>
      <Section title="Account">
        <Fields
          entries={[
            { label: 'Bank', value: orNA(data.bank_name) },
            { label: 'Account holder', value: orNA(data.account_holder) },
            { label: 'Account number', value: orNA(data.account_number), mono: true },
            { label: 'IFSC', value: orNA(data.ifsc_code), mono: true },
            { label: 'Period start', value: orNA(data.period_start) },
            { label: 'Period end', value: orNA(data.period_end) },
          ]}
        />
      </Section>

      <Section title={`Transactions (${txns.length})`}>
        {txns.length > 0 ? (
          <Table>
            <thead>
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Description</th>
                <th scope="col">Ref</th>
                <th scope="col" className={styles.num}>Debit</th>
                <th scope="col" className={styles.num}>Credit</th>
                <th scope="col" className={styles.num}>Balance</th>
              </tr>
            </thead>
            <tbody>
              {txns.map((txn, idx) => (
                <tr key={idx}>
                  <td className={styles.nowrap}>{txn.date || ''}</td>
                  <td>{txn.description || 'Transaction'}</td>
                  <td className={styles.muted}>{txn.cheque_ref_no || ''}</td>
                  <td className={styles.num}>{txn.debit ? formatInr(txn.debit) : ''}</td>
                  <td className={styles.num}>{txn.credit ? formatInr(txn.credit) : ''}</td>
                  <td className={styles.num}>{formatInr(txn.balance)}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        ) : (
          <p className={styles.none}>No transactions were extracted.</p>
        )}
      </Section>

      <Section title="Balances">
        <Totals
          rows={[
            { label: 'Opening balance', value: formatRupees(data.opening_balance) },
            { label: 'Total debits', value: formatRupees(debits) },
            { label: 'Total credits', value: formatRupees(credits) },
            { label: 'Closing balance', value: formatRupees(data.closing_balance), strong: true },
          ]}
        />
      </Section>
    </>
  );
};

// ── GST return ────────────────────────────────────────────────────────────

const ITCTable: React.FC<{
  title: string;
  rows: { label: string; breakdown?: GSTReturn['itc_available'] }[];
}> = ({ title, rows }) => (
  <Section title={title}>
    <Table>
      <thead>
        <tr>
          <th scope="col">Head</th>
          <th scope="col" className={styles.num}>IGST</th>
          <th scope="col" className={styles.num}>CGST</th>
          <th scope="col" className={styles.num}>SGST</th>
          <th scope="col" className={styles.num}>Cess</th>
          <th scope="col" className={styles.num}>Total</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.label}>
            <td>{row.label}</td>
            <td className={styles.num}>{formatInr(row.breakdown?.igst)}</td>
            <td className={styles.num}>{formatInr(row.breakdown?.cgst)}</td>
            <td className={styles.num}>{formatInr(row.breakdown?.sgst)}</td>
            <td className={styles.num}>{formatInr(row.breakdown?.cess)}</td>
            <td className={`${styles.num} ${styles.strong}`}>{formatRupees(row.breakdown?.total)}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  </Section>
);

export const GSTReturnView: React.FC<{ data: Partial<GSTReturn> }> = ({ data }) => (
  <>
    <Section title="Return">
      <Fields
        entries={[
          { label: 'Return type', value: orNA(data.return_type) },
          { label: 'Return period', value: orNA(data.return_period) },
          { label: 'GSTIN', value: orNA(data.gstin), mono: true },
          { label: 'ARN', value: orNA(data.arn_number), mono: true },
          { label: 'Legal name', value: orNA(data.legal_name ?? data.trade_name) },
          { label: 'Filing date', value: orNA(data.filing_date) },
        ]}
      />
    </Section>

    <ITCTable
      title="Input tax credit"
      rows={[
        { label: 'Available', breakdown: data.itc_available },
        { label: 'Reversed', breakdown: data.itc_reversed },
        { label: 'Net', breakdown: data.net_itc },
      ]}
    />

    <Section title="Outward supplies">
      <Totals
        rows={[
          { label: 'Taxable turnover', value: formatRupees(data.taxable_turnover) },
          { label: 'IGST', value: formatRupees(data.outward_tax_summary?.igst) },
          { label: 'CGST', value: formatRupees(data.outward_tax_summary?.cgst) },
          { label: 'SGST', value: formatRupees(data.outward_tax_summary?.sgst) },
          { label: 'Cess', value: formatRupees(data.outward_tax_summary?.cess) },
        ]}
      />
    </Section>
  </>
);

// ── TDS form ──────────────────────────────────────────────────────────────

export const TDSFormView: React.FC<{ data: Partial<TDSForm> }> = ({ data }) => {
  const deductions = data.section_deductions ?? [];
  const isForm16 = data.form_type === 'Form 16';

  return (
    <>
      <Section title="Certificate">
        <Fields
          entries={[
            { label: 'Form', value: orNA(data.form_type) },
            { label: 'Financial year', value: orNA(data.financial_year) },
            { label: 'Deductee PAN', value: orNA(data.pan), mono: true },
            { label: 'Deductor TAN', value: orNA(data.tan_of_deductor), mono: true },
            { label: 'Deductor name', value: orNA(data.deductor_name) },
            { label: 'Assessment year', value: orNA(data.assessment_year) },
          ]}
        />
      </Section>

      <Section title={`Deductions by section (${deductions.length})`}>
        {deductions.length > 0 ? (
          <Table>
            <thead>
              <tr>
                <th scope="col">Section</th>
                <th scope="col" className={styles.num}>Paid or credited</th>
                <th scope="col" className={styles.num}>TDS deducted</th>
                <th scope="col" className={styles.num}>TDS deposited</th>
              </tr>
            </thead>
            <tbody>
              {deductions.map((row, idx) => (
                <tr key={idx}>
                  <td>{orNA(row.section_code)}</td>
                  <td className={styles.num}>{formatRupees(row.amount_paid_credited)}</td>
                  <td className={styles.num}>{formatRupees(row.tds_deducted)}</td>
                  <td className={styles.num}>{formatRupees(row.tds_deposited)}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        ) : (
          <p className={styles.none}>No section-wise deductions were extracted.</p>
        )}
      </Section>

      <Section title="Totals">
        <Totals
          rows={[
            {
              label: isForm16 ? 'Gross salary' : 'Total amount credited',
              value: formatRupees(isForm16 ? data.gross_salary : data.total_amount_credited),
            },
            { label: 'TDS deducted', value: formatRupees(data.total_tds_deducted) },
            { label: 'TDS deposited', value: formatRupees(data.total_tds_deposited), strong: true },
          ]}
        />
      </Section>
    </>
  );
};

// ── Investment proof ──────────────────────────────────────────────────────

export const InvestmentProofView: React.FC<{ data: Partial<InvestmentProof> }> = ({ data }) => (
  <>
    <Section title="Investment">
      <Fields
        entries={[
          { label: 'Section', value: orNA(data.section) },
          { label: 'Amount paid', value: formatRupees(data.amount_paid) },
          { label: 'Taxpayer', value: orNA(data.taxpayer_name) },
          { label: 'PAN', value: orNA(data.pan), mono: true },
          { label: 'Institution', value: orNA(data.institution_name) },
          { label: 'Policy or account no.', value: orNA(data.policy_account_no), mono: true },
          { label: 'Date of payment', value: orNA(data.date_of_payment) },
          { label: 'Mode of payment', value: orNA(data.mode_of_payment) },
          { label: 'Financial year', value: orNA(data.financial_year) },
          { label: 'Notes', value: orNA(data.notes) },
        ]}
      />
    </Section>

    <Section title="Claim">
      <Totals
        rows={[
          {
            label: `Eligible amount, section ${orNA(data.section)}`,
            value: formatRupees(data.amount_paid),
            strong: true,
          },
        ]}
      />
    </Section>
  </>
);
