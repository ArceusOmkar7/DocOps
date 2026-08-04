import { DocumentType, WorkflowType } from '../types/enums';
import { WorkflowRequirementCreate } from '../types/api';

export interface WorkflowTemplate {
  id: string;
  name: string;
  type: WorkflowType;
  description: string;
  category: 'Tax & Compliance' | 'Finance & AP' | 'Audit' | 'HR';
  icon: string;
  requirements: WorkflowRequirementCreate[];
}

export const WORKFLOW_TEMPLATES: WorkflowTemplate[] = [
  {
    id: 'gst_filing',
    name: 'GST Monthly Filing (GSTR-3B & 1)',
    type: WorkflowType.GST_FILING,
    category: 'Tax & Compliance',
    description:
      'Automated GSTR-3B reconciliation. Collects inward purchase bills, outward sales invoices, bank statements, and GSTR-2B JSON to detect tax mismatches and notify defaulting suppliers.',
    icon: 'ReceiptIndianRupee',
    requirements: [
      {
        document_type: DocumentType.INVOICE,
        label: 'Purchase Bills (Inward Tax Invoices)',
        required_count: 12,
        notes: 'All vendor/supplier invoices for the current period',
      },
      {
        document_type: DocumentType.INVOICE,
        label: 'Sales Invoices (Outward Tax Invoices)',
        required_count: 15,
        notes: 'All customer invoices issued during the period',
      },
      {
        document_type: DocumentType.BANK_STATEMENT,
        label: 'Bank Statement',
        required_count: 1,
        notes: 'Primary business bank statement for payment reconciliation',
      },
      {
        document_type: DocumentType.GST_RETURN,
        label: 'GSTR-2B Auto-Drafted JSON',
        required_count: 1,
        notes: 'Portal GSTR-2B statement to verify Input Tax Credit eligibility',
      },
    ],
  },
  {
    id: 'ap_3way_match',
    name: 'Accounts Payable 3-Way Invoice Matching',
    type: WorkflowType.BOOKKEEPING,
    category: 'Finance & AP',
    description: 'Autonomous 3-way matching between Purchase Order, Goods Receipt Note (GRN), and Vendor Invoice. Auto-approves matching invoices or flags price/qty variance for review.',
    icon: 'GitCompare',
    requirements: [
      {
        document_type: DocumentType.PURCHASE_ORDER,
        label: 'Authorized Purchase Order (PO)',
        required_count: 1,
        notes: 'Contains approved items, agreed unit prices, and delivery schedule',
      },
      {
        document_type: DocumentType.RECEIPT,
        label: 'Goods Receipt Note (GRN) / Delivery Challan',
        required_count: 1,
        notes: 'Proof of physical receipt and quality acceptance',
      },
      {
        document_type: DocumentType.INVOICE,
        label: 'Vendor Tax Invoice',
        required_count: 1,
        notes: 'Final invoice submitted by the vendor',
      },
    ],
  },
  {
    id: 'monthly_bookkeeping',
    name: 'Monthly Bookkeeping & Closing',
    type: WorkflowType.BOOKKEEPING,
    category: 'Finance & AP',
    description: 'Monthly books closure workflow for accountants. Aggregates all financial records to prepare trial balance and profit/loss statements.',
    icon: 'BookOpen',
    requirements: [
      {
        document_type: DocumentType.INVOICE,
        label: 'Sales & Revenue Invoices',
        required_count: 10,
        notes: 'All customer billings for the month',
      },
      {
        document_type: DocumentType.INVOICE,
        label: 'Vendor Bills & Expenses',
        required_count: 15,
        notes: 'Operational bills, utility bills, rent invoices',
      },
      {
        document_type: DocumentType.BANK_STATEMENT,
        label: 'Bank Account Statements',
        required_count: 2,
        notes: 'Statements for all operational bank accounts',
      },
      {
        document_type: DocumentType.RECEIPT,
        label: 'Petty Cash & Expense Vouchers',
        required_count: 5,
        notes: 'Cash receipts and minor expense vouchers',
      },
    ],
  },
  {
    id: 'tds_quarterly',
    name: 'Quarterly TDS Return (Form 26Q / 24Q)',
    type: WorkflowType.TDS_FILING,
    category: 'Tax & Compliance',
    description: 'Collect Form 16A certificates, TDS payment challans, and deduction registers to generate quarter-end tax deduction returns.',
    icon: 'Building2',
    requirements: [
      {
        document_type: DocumentType.INVOICE,
        label: 'TDS Deductible Vendor Bills',
        required_count: 8,
        notes: 'Invoices under Sec 194C, 194J, 194I',
      },
      {
        document_type: DocumentType.RECEIPT,
        label: 'TDS Deposit Challans (ITNS 281)',
        required_count: 3,
        notes: 'Monthly challan receipts paid to government treasury',
      },
      {
        document_type: DocumentType.BANK_STATEMENT,
        label: 'Bank Statement (TDS Debits)',
        required_count: 1,
        notes: 'Bank proof of tax remittance',
      },
    ],
  },
];
