import React from 'react';
import type {
  BankStatement,
  GSTReturn,
  InvestmentProof,
  TDSForm,
} from '../../types/api';
import styles from './DocumentDrawer.module.css';

const fmtINR = (value?: number | null): string =>
  value != null ? value.toLocaleString('en-IN') : '0';

const orNA = (value?: string | number | null): string =>
  value == null || value === '' ? 'N/A' : String(value);

interface InfoEntry {
  label: string;
  value: React.ReactNode;
  highlight?: boolean;
}

const InfoGrid: React.FC<{ entries: InfoEntry[] }> = ({ entries }) => (
  <div className={styles.infoGrid}>
    {entries.map((entry) => (
      <div key={entry.label} className={styles.infoItem}>
        <span className={styles.infoLabel}>{entry.label}</span>
        <span className={entry.highlight ? styles.infoValueHighlight : styles.infoValue}>
          {entry.value}
        </span>
      </div>
    ))}
  </div>
);

// ── Bank Statement ────────────────────────────────────────────────────────

export const BankStatementView: React.FC<{ data: Partial<BankStatement> }> = ({ data }) => {
  const txns = data.transactions ?? [];
  return (
    <>
      <div className={styles.section}>
        <div className={styles.sectionHeader}>Account Details</div>
        <InfoGrid
          entries={[
            { label: 'Bank', value: orNA(data.bank_name) },
            { label: 'Account Number', value: orNA(data.account_number) },
            { label: 'IFSC Code', value: orNA(data.ifsc_code), highlight: true },
            { label: 'Account Holder', value: orNA(data.account_holder) },
            { label: 'Period Start', value: orNA(data.period_start) },
            { label: 'Period End', value: orNA(data.period_end) },
          ]}
        />
      </div>

      <div className={styles.section}>
        <div className={styles.sectionHeader}>Transactions ({txns.length})</div>
        {txns.length > 0 ? (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th style={{ width: 90 }}>Date</th>
                  <th>Description</th>
                  <th>Ref No</th>
                  <th style={{ textAlign: 'right' }}>Debit</th>
                  <th style={{ textAlign: 'right' }}>Credit</th>
                  <th style={{ textAlign: 'right' }}>Balance</th>
                </tr>
              </thead>
              <tbody>
                {txns.map((txn, idx) => (
                  <tr key={idx}>
                    <td style={{ whiteSpace: 'nowrap', color: '#64748b' }}>{txn.date || '—'}</td>
                    <td style={{ fontWeight: 500, color: '#0f172a' }}>
                      {txn.description || 'Transaction'}
                    </td>
                    <td style={{ color: '#94a3b8' }}>{txn.cheque_ref_no || '—'}</td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap', color: '#dc2626' }}>
                      {txn.debit ? `₹${fmtINR(txn.debit)}` : '—'}
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap', color: '#059669' }}>
                      {txn.credit ? `₹${fmtINR(txn.credit)}` : '—'}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 600, whiteSpace: 'nowrap' }}>
                      ₹{fmtINR(txn.balance)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className={styles.emptyState}>No transactions extracted.</div>
        )}
      </div>

      <div className={styles.section}>
        <div className={styles.taxSummaryGrid}>
          <div className={styles.summaryBlock}>
            <div className={styles.taxBlockTitle}>Balance Summary</div>
            <div className={styles.summaryRow}>
              <span>Opening Balance</span>
              <span>₹{fmtINR(data.opening_balance)}</span>
            </div>
            <div className={styles.totalRow}>
              <span>Closing Balance</span>
              <span>₹{fmtINR(data.closing_balance)}</span>
            </div>
          </div>
          <div className={styles.summaryBlock}>
            <div className={styles.taxBlockTitle}>Flow Summary</div>
            <div className={styles.summaryRow}>
              <span>Total Debits</span>
              <span style={{ color: '#dc2626' }}>
                ₹{fmtINR(txns.reduce((sum, t) => sum + (t.debit ?? 0), 0))}
              </span>
            </div>
            <div className={styles.totalRow}>
              <span>Total Credits</span>
              <span style={{ color: '#059669' }}>
                ₹{fmtINR(txns.reduce((sum, t) => sum + (t.credit ?? 0), 0))}
              </span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

// ── GST Return ────────────────────────────────────────────────────────────

const ITCGrid: React.FC<{
  title: string;
  rows: { label: string; breakdown?: GSTReturn['itc_available'] }[];
}> = ({ title, rows }) => (
  <div className={styles.section}>
    <div className={styles.sectionHeader}>{title}</div>
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Head</th>
            <th style={{ textAlign: 'right' }}>IGST</th>
            <th style={{ textAlign: 'right' }}>CGST</th>
            <th style={{ textAlign: 'right' }}>SGST</th>
            <th style={{ textAlign: 'right' }}>Cess</th>
            <th style={{ textAlign: 'right' }}>Total</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td style={{ fontWeight: 600 }}>{row.label}</td>
              <td style={{ textAlign: 'right' }}>{fmtINR(row.breakdown?.igst)}</td>
              <td style={{ textAlign: 'right' }}>{fmtINR(row.breakdown?.cgst)}</td>
              <td style={{ textAlign: 'right' }}>{fmtINR(row.breakdown?.sgst)}</td>
              <td style={{ textAlign: 'right' }}>{fmtINR(row.breakdown?.cess)}</td>
              <td style={{ textAlign: 'right', fontWeight: 700, color: '#4f46e5' }}>
                ₹{fmtINR(row.breakdown?.total)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export const GSTReturnView: React.FC<{ data: Partial<GSTReturn> }> = ({ data }) => (
  <>
    <div className={styles.section}>
      <div className={styles.sectionHeader}>Return Details</div>
      <InfoGrid
        entries={[
          { label: 'Return Type', value: orNA(data.return_type), highlight: true },
          { label: 'GSTIN', value: orNA(data.gstin) },
          { label: 'Return Period', value: orNA(data.return_period) },
          { label: 'Filing Date', value: orNA(data.filing_date) },
          { label: 'ARN Number', value: orNA(data.arn_number) },
          { label: 'Legal Name', value: orNA(data.legal_name ?? data.trade_name) },
        ]}
      />
    </div>

    <ITCGrid
      title="Input Tax Credit (ITC)"
      rows={[
        { label: 'ITC Available', breakdown: data.itc_available },
        { label: 'ITC Reversed', breakdown: data.itc_reversed },
        { label: 'Net ITC', breakdown: data.net_itc },
      ]}
    />

    <div className={styles.section}>
      <div className={styles.taxSummaryGrid}>
        <div className={styles.taxBlock}>
          <div className={styles.taxBlockTitle}>Outward Tax Summary</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>IGST</span>
              <span style={{ fontWeight: 600 }}>₹{fmtINR(data.outward_tax_summary?.igst)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>CGST</span>
              <span style={{ fontWeight: 600 }}>₹{fmtINR(data.outward_tax_summary?.cgst)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>SGST</span>
              <span style={{ fontWeight: 600 }}>₹{fmtINR(data.outward_tax_summary?.sgst)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Cess</span>
              <span style={{ fontWeight: 600 }}>₹{fmtINR(data.outward_tax_summary?.cess)}</span>
            </div>
          </div>
        </div>
        <div className={styles.summaryBlock}>
          <div className={styles.taxBlockTitle}>Turnover</div>
          <div className={styles.totalRow} style={{ border: 'none', padding: 0, marginTop: 8 }}>
            <span>Taxable Turnover</span>
            <span>₹{fmtINR(data.taxable_turnover)}</span>
          </div>
        </div>
      </div>
    </div>
  </>
);

// ── TDS Form ──────────────────────────────────────────────────────────────

export const TDSFormView: React.FC<{ data: Partial<TDSForm> }> = ({ data }) => {
  const deductions = data.section_deductions ?? [];
  return (
    <>
      <div className={styles.section}>
        <div className={styles.sectionHeader}>Certificate Details</div>
        <InfoGrid
          entries={[
            { label: 'Form Type', value: orNA(data.form_type), highlight: true },
            { label: 'PAN (Deductee)', value: orNA(data.pan) },
            { label: 'TAN of Deductor', value: orNA(data.tan_of_deductor) },
            { label: 'Deductor Name', value: orNA(data.deductor_name) },
            { label: 'Financial Year', value: orNA(data.financial_year) },
            { label: 'Assessment Year', value: orNA(data.assessment_year) },
          ]}
        />
      </div>

      <div className={styles.section}>
        <div className={styles.sectionHeader}>Section-wise Deductions ({deductions.length})</div>
        {deductions.length > 0 ? (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Section</th>
                  <th style={{ textAlign: 'right' }}>Amount Paid/Credited</th>
                  <th style={{ textAlign: 'right' }}>TDS Deducted</th>
                  <th style={{ textAlign: 'right' }}>TDS Deposited</th>
                </tr>
              </thead>
              <tbody>
                {deductions.map((row, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 700, color: '#4f46e5' }}>
                      {orNA(row.section_code)}
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      ₹{fmtINR(row.amount_paid_credited)}
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      ₹{fmtINR(row.tds_deducted)}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 600, whiteSpace: 'nowrap' }}>
                      ₹{fmtINR(row.tds_deposited)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className={styles.emptyState}>No section-wise deductions extracted.</div>
        )}
      </div>

      <div className={styles.section}>
        <div className={styles.taxSummaryGrid}>
          <div className={styles.summaryBlock}>
            <div className={styles.taxBlockTitle}>Income</div>
            <div className={styles.summaryRow}>
              <span>{data.form_type === 'Form 16' ? 'Gross Salary' : 'Total Amount Credited'}</span>
              <span>
                ₹{fmtINR(data.form_type === 'Form 16' ? data.gross_salary : data.total_amount_credited)}
              </span>
            </div>
          </div>
          <div className={styles.summaryBlock}>
            <div className={styles.taxBlockTitle}>Tax Deducted at Source</div>
            <div className={styles.summaryRow}>
              <span>TDS Deducted</span>
              <span>₹{fmtINR(data.total_tds_deducted)}</span>
            </div>
            <div className={styles.totalRow}>
              <span>TDS Deposited</span>
              <span>₹{fmtINR(data.total_tds_deposited)}</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

// ── Investment Proof ──────────────────────────────────────────────────────

export const InvestmentProofView: React.FC<{ data: Partial<InvestmentProof> }> = ({ data }) => (
  <>
    <div className={styles.section}>
      <div className={styles.sectionHeader}>Investment Details</div>
      <InfoGrid
        entries={[
          { label: 'Section', value: orNA(data.section), highlight: true },
          { label: 'Amount Paid', value: `₹${fmtINR(data.amount_paid)}` },
          { label: 'Taxpayer Name', value: orNA(data.taxpayer_name) },
          { label: 'PAN', value: orNA(data.pan) },
          { label: 'Institution', value: orNA(data.institution_name) },
          { label: 'Policy/Account No', value: orNA(data.policy_account_no) },
          { label: 'Date of Payment', value: orNA(data.date_of_payment) },
          { label: 'Mode of Payment', value: orNA(data.mode_of_payment) },
          { label: 'Financial Year', value: orNA(data.financial_year) },
          { label: 'Notes', value: orNA(data.notes) },
        ]}
      />
    </div>

    <div className={styles.section}>
      <div className={styles.taxSummaryGrid}>
        <div className={styles.summaryBlock}>
          <div className={styles.taxBlockTitle}>Claim Under Chapter VI-A</div>
          <div className={styles.totalRow} style={{ border: 'none', padding: 0, marginTop: 8 }}>
            <span>Eligible Amount (Section {orNA(data.section)})</span>
            <span>₹{fmtINR(data.amount_paid)}</span>
          </div>
        </div>
      </div>
    </div>
  </>
);
