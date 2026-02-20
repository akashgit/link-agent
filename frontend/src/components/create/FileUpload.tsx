"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/Button";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  accepted?: string;
}

export function FileUpload({ onFileSelect, accepted = ".pdf,.pptx,.txt" }: FileUploadProps) {
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Upload Reference (optional)</label>
      <div className="flex items-center gap-3">
        <Button type="button" variant="secondary" size="sm" onClick={() => inputRef.current?.click()}>
          Choose File
        </Button>
        <span className="text-sm text-gray-500">{fileName || "No file selected"}</span>
        <input ref={inputRef} type="file" accept={accepted} onChange={handleChange} className="hidden" />
      </div>
      <p className="text-xs text-gray-400">Supports PDF, PPTX, TXT</p>
    </div>
  );
}
