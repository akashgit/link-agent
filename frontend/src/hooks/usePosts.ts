"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchPosts, fetchPost, createPost, updatePost, deletePost, fetchPostVersions } from "@/lib/api";
import type { Post, PostWithDrafts, Draft } from "@/lib/types";

export function usePosts(params?: Record<string, string>) {
  return useQuery<Post[]>({
    queryKey: ["posts", params],
    queryFn: () => fetchPosts(params),
  });
}

export function usePost(id: string) {
  return useQuery<PostWithDrafts>({
    queryKey: ["post", id],
    queryFn: () => fetchPost(id),
    enabled: !!id,
  });
}

export function usePostVersions(id: string) {
  return useQuery<Draft[]>({
    queryKey: ["post-versions", id],
    queryFn: () => fetchPostVersions(id),
    enabled: !!id,
  });
}

export function useCreatePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createPost,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["posts"] }),
  });
}

export function useUpdatePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      updatePost(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: ["posts"] });
      qc.invalidateQueries({ queryKey: ["post", id] });
    },
  });
}

export function useDeletePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deletePost,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["posts"] }),
  });
}
