import React, { useRef, useState } from 'react';
import { FileUp, Loader2 } from 'lucide-react';
import { useParseDocument, useUploadDocument } from '../../hooks/useOCR';
import ui from '../../styles/ui.module.css';
import styles from './DocumentUploader.module.css';

interface DocumentUploaderProps {
  onSuccess?: () => void;
  clientId?: string;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onSuccess, clientId }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useUploadDocument();
  const parseMutation = useParseDocument();

  const isProcessing = uploadMutation.isPending || parseMutation.isPending;

  const handleFile = async (file: File) => {
    setError('');
    try {
      // Step 1: layout-aware OCR
      const ocrResult = await uploadMutation.mutateAsync(file);

      // Step 2: classify and extract into a typed business object
      const resId = ocrResult.result_id || ocrResult.id;
      if (!resId) {
        throw new Error('OCR returned no result ID');
      }
      await parseMutation.mutateAsync({ resultId: resId, clientId });

      onSuccess?.();
    } catch (err) {
      setError(
        err instanceof Error
          ? `${file.name} could not be processed: ${err.message}`
          : `${file.name} could not be processed.`
      );
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
    <div>
      <button
        type="button"
        className={`${styles.dropzone} ${dragActive ? styles.active : ''}`}
        disabled={isProcessing}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        {isProcessing ? (
          <Loader2 size={20} className={ui.spin} aria-hidden="true" />
        ) : (
          <FileUp size={20} strokeWidth={1.75} aria-hidden="true" />
        )}
        <span className={styles.text}>
          <span className={styles.title}>
            {isProcessing ? 'Reading the document. This can take a minute.' : 'Drop a file here, or choose one'}
          </span>
          <span className={styles.subtitle}>PDF, PNG, JPG, TIFF or BMP, up to 20 MB</span>
        </span>
      </button>

      <input
        ref={fileInputRef}
        type="file"
        className={styles.fileInput}
        accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
        tabIndex={-1}
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
            e.target.value = '';
          }
        }}
      />

      {error && (
        <p className={ui.errorText} role="alert" style={{ marginTop: 8 }}>
          {error}
        </p>
      )}
    </div>
  );
};
