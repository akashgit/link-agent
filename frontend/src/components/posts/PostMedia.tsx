"use client";

import { useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { fetchPostMedia, uploadPostMedia, deletePostMedia, getFileUrl } from "@/lib/api";
import type { MediaAsset } from "@/lib/types";

const SOURCE_LABELS: Record<string, { label: string; className: string }> = {
  generated: { label: "Generated", className: "bg-purple-100 text-purple-700" },
  extracted: { label: "Extracted", className: "bg-blue-100 text-blue-700" },
  uploaded: { label: "Uploaded", className: "bg-gray-100 text-gray-600" },
  web_retrieved: { label: "Web", className: "bg-green-100 text-green-700" },
};

interface PostMediaProps {
  postId: string;
}

export function PostMedia({ postId }: PostMediaProps) {
  const queryClient = useQueryClient();
  const [uploading, setUploading] = useState(false);

  const { data: media = [], isLoading } = useQuery<MediaAsset[]>({
    queryKey: ["post-media", postId],
    queryFn: () => fetchPostMedia(postId),
  });

  const deleteMutation = useMutation({
    mutationFn: (assetId: string) => deletePostMedia(postId, assetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["post-media", postId] });
    },
  });

  const handleFileChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setUploading(true);
      try {
        await uploadPostMedia(postId, file);
        queryClient.invalidateQueries({ queryKey: ["post-media", postId] });
      } finally {
        setUploading(false);
        e.target.value = "";
      }
    },
    [postId, queryClient],
  );

  const imageAssets = media.filter((a) => a.content_type.startsWith("image/"));

  if (isLoading) {
    return (
      <Card>
        <div className="flex justify-center py-4">
          <Spinner size="sm" />
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-gray-700">Media ({imageAssets.length})</h4>
        <label className="cursor-pointer inline-flex items-center justify-center rounded-lg font-medium text-sm px-3 py-1.5 text-gray-600 hover:bg-gray-100 transition-colors">
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
            disabled={uploading}
          />
          {uploading ? "Uploading..." : "Upload"}
        </label>
      </div>

      {imageAssets.length === 0 ? (
        <p className="text-xs text-gray-400">No media attached yet.</p>
      ) : (
        <div className="grid grid-cols-2 gap-2">
          {imageAssets.map((asset) => {
            const sourceInfo = SOURCE_LABELS[asset.source || "uploaded"] || SOURCE_LABELS.uploaded;
            return (
              <div key={asset.id} className="relative group rounded-lg overflow-hidden border border-gray-200">
                <img
                  src={getFileUrl(`/api/uploads/file/${asset.file_path.split("/").pop()}`)}
                  alt={asset.filename}
                  className="w-full h-24 object-cover"
                />
                <div className="absolute top-1 left-1">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${sourceInfo.className}`}>
                    {sourceInfo.label}
                  </span>
                </div>
                <button
                  onClick={() => deleteMutation.mutate(asset.id)}
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Delete"
                >
                  x
                </button>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
