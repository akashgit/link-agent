"use client";

import { CreatePostForm } from "@/components/create/CreatePostForm";

export default function CreatePage() {
  return (
    <div>
      <p className="text-gray-500 mb-6">Follow the wizard to generate an AI-powered LinkedIn post.</p>
      <CreatePostForm />
    </div>
  );
}
