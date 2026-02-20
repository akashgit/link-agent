"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { PillarSelector } from "./PillarSelector";
import { FormatSelector } from "./FormatSelector";
import { FileUpload } from "./FileUpload";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Card } from "@/components/ui/Card";
import { useCreatePost } from "@/hooks/usePosts";
import { useRunAgent } from "@/hooks/useAgent";
import { uploadFile } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

export function CreatePostForm() {
  const router = useRouter();
  const createPost = useCreatePost();
  const runAgent = useRunAgent();
  const { toast } = useToast();

  const [step, setStep] = useState(0);
  const [pillar, setPillar] = useState("");
  const [format, setFormat] = useState("");
  const [title, setTitle] = useState("");
  const [userInput, setUserInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const canProceed = [
    !!pillar,
    !!format,
    !!title,
    true, // step 3 is always valid
  ];

  const handleGenerate = async () => {
    setLoading(true);
    try {
      let uploadedText: string | undefined;
      if (file) {
        await uploadFile(file);
      }

      const post = await createPost.mutateAsync({
        title,
        content_pillar: pillar,
        post_format: format,
        user_input: userInput || undefined,
      });

      const agentResult = await runAgent.mutateAsync({
        post_id: post.id,
        user_input: userInput || title,
        content_pillar: pillar,
        post_format: format,
        uploaded_file_text: uploadedText,
      });

      toast("Agent started! Redirecting to post detail...", "success");
      router.push(`/posts/${post.id}`);
    } catch (err) {
      toast("Failed to start agent. Check your backend connection.", "error");
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    <PillarSelector key="pillar" selected={pillar} onChange={setPillar} />,
    <FormatSelector key="format" selected={format} onChange={setFormat} />,
    <div key="input" className="space-y-4">
      <Input label="Post Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. 3 Layers of Agent Reliability" />
      <Textarea label="Topic / Key Ideas" value={userInput} onChange={(e) => setUserInput(e.target.value)} placeholder="What should this post be about? Any specific angles or points to cover?" rows={6} />
    </div>,
    <div key="upload" className="space-y-4">
      <FileUpload onFileSelect={setFile} />
      <Card className="bg-gray-50">
        <h4 className="font-medium text-sm mb-2">Summary</h4>
        <dl className="text-sm space-y-1">
          <div className="flex justify-between"><dt className="text-gray-500">Pillar:</dt><dd className="font-medium">{pillar.replace("_", " ")}</dd></div>
          <div className="flex justify-between"><dt className="text-gray-500">Format:</dt><dd className="font-medium">{format.replace("_", " ")}</dd></div>
          <div className="flex justify-between"><dt className="text-gray-500">Title:</dt><dd className="font-medium">{title}</dd></div>
          {file && <div className="flex justify-between"><dt className="text-gray-500">File:</dt><dd className="font-medium">{file.name}</dd></div>}
        </dl>
      </Card>
    </div>,
  ];

  return (
    <div className="max-w-xl mx-auto">
      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        {["Pillar", "Format", "Content", "Generate"].map((label, i) => (
          <div key={label} className="flex items-center gap-2 flex-1">
            <div className={`h-2 flex-1 rounded-full ${i <= step ? "bg-blue-500" : "bg-gray-200"}`} />
          </div>
        ))}
      </div>
      <div className="flex justify-between text-xs text-gray-500 mb-6 -mt-6">
        {["Pillar", "Format", "Content", "Generate"].map((label, i) => (
          <span key={label} className={i === step ? "text-blue-600 font-medium" : ""}>{label}</span>
        ))}
      </div>

      <Card>
        {steps[step]}

        <div className="flex justify-between mt-6 pt-4 border-t">
          <Button variant="ghost" onClick={() => setStep(step - 1)} disabled={step === 0}>
            Back
          </Button>
          {step < 3 ? (
            <Button onClick={() => setStep(step + 1)} disabled={!canProceed[step]}>
              Next
            </Button>
          ) : (
            <Button onClick={handleGenerate} loading={loading}>
              Generate Post
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}
