"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Search, Trash, Undo, X } from "lucide-react";
import { toast } from "sonner";

import { useWorkspaceStore } from "@/stores/workspace-store";
import { Input } from "@/components/ui/input";

export const TrashBox = () => {
  const router = useRouter();
  const params = useParams();
  const { 
    currentWorkspace, 
    trashPages, 
    fetchTrash, 
    restorePage, 
    deletePage 
  } = useWorkspaceStore();
  
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (currentWorkspace) {
      fetchTrash(currentWorkspace.id);
    }
  }, [currentWorkspace, fetchTrash]);

  const onClick = (pageId: string) => {
    router.push(`/dashboard/${pageId}`);
  };

  const onRestore = async (event: React.MouseEvent<HTMLDivElement, MouseEvent>, pageId: string) => {
    event.stopPropagation();
    const promise = restorePage(pageId);
    
    toast.promise(promise, {
      loading: "Restoring page...",
      success: "Page restored!",
      error: "Failed to restore page."
    });
  };

  const onRemove = async (pageId: string) => {
    const promise = deletePage(pageId);
    
    toast.promise(promise, {
      loading: "Deleting page...",
      success: "Page deleted!",
      error: "Failed to delete page."
    });

    if (params.pageId === pageId) {
      router.push("/dashboard");
    }
  };

  const filteredPages = trashPages.filter((page) => {
    return page.title.toLowerCase().includes(search.toLowerCase());
  });

  return (
    <div className="text-sm">
      <div className="flex items-center gap-x-1 p-2">
        <Search className="h-4 w-4" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-7 px-2 focus-visible:ring-transparent bg-secondary"
          placeholder="Filter by page title..."
        />
      </div>
      <div className="mt-2 px-1 pb-1">
        <p className="hidden last:block text-xs text-center text-muted-foreground pb-2">
          No documents found.
        </p>
        {filteredPages.map((page) => (
          <div
            key={page.id}
            role="button"
            onClick={() => onClick(page.id)}
            className="text-sm rounded-sm w-full hover:bg-primary/5 flex items-center text-primary justify-between"
          >
            <span className="truncate pl-2">
              {page.title}
            </span>
            <div className="flex items-center">
              <div
                role="button"
                onClick={(e) => onRestore(e, page.id)}
                className="rounded-sm p-2 hover:bg-neutral-200 dark:hover:bg-neutral-600"
              >
                <Undo className="h-4 w-4 text-muted-foreground" />
              </div>
              <div
                role="button"
                onClick={() => onRemove(page.id)}
                className="rounded-sm p-2 hover:bg-neutral-200 dark:hover:bg-neutral-600"
              >
                <Trash className="h-4 w-4 text-muted-foreground" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
