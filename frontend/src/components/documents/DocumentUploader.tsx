import React, { useRef, useState } from 'react';
import { FileUp, Loader2 } from 'lucide-react';
import { useParseDocument, useUploadDocument } from '../../hooks/useOCR';
import styles from './DocumentUploader.module.css';

interface DocumentUploaderProps {
  onSuccess?: () => void;
  clientId?: string;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onSuccess, clientId }) => {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useUploadDocument();
  const parseMutation = useParseDocument();

  const isProcessing = uploadMutation.isPending || parseMutation.isPending;

  const handleFile = async (file: File) => {
    try {
      // Step 1: Run PaddleOCR layout extraction
      const ocrResult = await uploadMutation.mutateAsync(file);

      // Step 2: Parse into business object via LLM
      await parseMutation.mutateAsync({
        resultId: ocrResult.id,
        clientId,
      });

      onSuccess?.();
    } catch (err) {
      console.error('Document processing failed:', err);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div
      className={`${styles.dropzone} ${dragActive ? styles.active : ''}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragActive(true);
      }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <input
        ref={fileInputRef}
        type="file"
        className={styles.fileInput}
        accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
          }
        }}
      />

      <div className={styles.iconCircle}>
        {isProcessing ? <Loader2 size={24} className="animate-spin" /> : <FileUp size={24} />}
      </div>

      <div className={styles.title}>
        {isProcessing
          ? 'Extracting Document Intelligence...'
          : 'Click or drag PDF / Image invoices to upload'}
      </div>

      <div className={styles.subtitle}>
        Supports PDF, PNG, JPG (up to 20MB). Auto-runs PaddleOCR layout + LLM extraction.
      </div>
    </div>
  );
};
