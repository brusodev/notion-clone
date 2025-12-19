"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { Page } from "@/types";
import { Editor } from "@/components/editor/Editor";
import { Cover } from "@/components/cover";

export default function PublicPage() {
  const params = useParams();
  const pageId = params.pageId as string;
  
  const [page, setPage] = useState<Page | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const loadPage = async () => {
      try {
        const response = await apiClient.get<Page & { blocks: any[] }>(`/public/pages/${pageId}`);
        setPage(response.data);
      } catch (error) {
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };
    loadPage();
  }, [pageId]);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center dark:bg-[#1F1F1F]">
        <p>Loading...</p>
      </div>
    );
  }

  if (error || !page) {
    return (
      <div className="h-full flex items-center justify-center dark:bg-[#1F1F1F]">
        <p>Page not found or is private.</p>
      </div>
    );
  }

  // @ts-ignore
  const contentBlock = page.blocks?.find((b: any) => b.type === "editor_content");
  const initialContent = contentBlock?.content?.html || "";

  return (
    <div className="min-h-full flex flex-col dark:bg-[#1F1F1F]">
      <Cover preview url={page.cover_image} />
      <div className="md:max-w-3xl lg:max-w-4xl mx-auto w-full px-10 py-10">
        <div className="text-4xl font-bold pb-4 flex items-center gap-x-4">
          {page.icon && <span>{page.icon}</span>}
          {page.title}
        </div>
        <Editor 
          editable={false}
          initialContent={initialContent}
        />
      </div>
    </div>
  );
}
