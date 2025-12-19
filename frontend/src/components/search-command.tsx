"use client";

import { useEffect, useState } from "react";
import { File, Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useSearch } from "@/hooks/use-search";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { apiClient } from "@/lib/api-client";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";

interface SearchResult {
  page_id: string;
  page_title: string;
  page_icon?: string;
  highlight: string;
  matched_in: "title" | "content";
  matched_blocks: Array<{
    block_id: string;
    content_text: string;
    highlight: string;
  }>;
}

export const SearchCommand = () => {
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);
  const toggle = useSearch((store) => store.toggle);
  const isOpen = useSearch((store) => store.isOpen);
  const onClose = useSearch((store) => store.onClose);
  const { currentWorkspace } = useWorkspaceStore();
  
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        toggle();
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [toggle]);

  useEffect(() => {
    const search = async () => {
      if (!query || !currentWorkspace) {
        setResults([]);
        return;
      }

      setIsLoading(true);
      try {
        const response = await apiClient.post("/search/", {
          query,
          workspace_id: currentWorkspace.id,
          limit: 10
        });
        setResults(response.data.results);
      } catch (error) {
        console.error("Search failed", error);
      } finally {
        setIsLoading(false);
      }
    };

    const debounce = setTimeout(search, 300);
    return () => clearTimeout(debounce);
  }, [query, currentWorkspace]);

  const onSelect = (id: string) => {
    router.push(`/dashboard/${id}`);
    onClose();
  };

  if (!isMounted) {
    return null;
  }

  return (
    <CommandDialog open={isOpen} onOpenChange={onClose}>
      <CommandInput
        placeholder={`Search ${currentWorkspace?.name || "..."}`}
        value={query}
        onValueChange={setQuery}
      />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        {results.length > 0 && (
          <CommandGroup heading="Pages">
            {results.map((result) => (
              <CommandItem
                key={result.page_id}
                value={`${result.page_id}-${result.page_title}`}
                title={result.page_title}
                onSelect={() => onSelect(result.page_id)}
              >
                {result.page_icon ? (
                  <span className="mr-2 text-[18px]">{result.page_icon}</span>
                ) : (
                  <File className="mr-2 h-4 w-4" />
                )}
                <div className="flex flex-col">
                  <span dangerouslySetInnerHTML={{ __html: result.matched_in === 'title' ? result.highlight : result.page_title }} />
                  {result.matched_blocks.length > 0 && (
                    <span 
                      className="text-xs text-muted-foreground line-clamp-1"
                      dangerouslySetInnerHTML={{ __html: result.matched_blocks[0].highlight }} 
                    />
                  )}
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        )}
      </CommandList>
    </CommandDialog>
  );
};
