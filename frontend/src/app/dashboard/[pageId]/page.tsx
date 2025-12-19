"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { Editor } from "@/components/editor/Editor";
import { Page } from "@/types";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Smile, ImageIcon, X, Star } from "lucide-react";
import { Cover } from "@/components/cover";
import { IconPicker } from "@/components/icon-picker";
import { Publish } from "@/components/publish";
import { cn } from "@/lib/utils";
import { useCoverImage } from "@/hooks/use-cover-image";

export default function PageEditor() {
  const params = useParams();
  const pageId = params.pageId as string;
  const coverImage = useCoverImage();
  const { 
    getPage, 
    updatePage, 
    fetchPageBlocks, 
    savePageContent,
    addFavorite,
    removeFavorite,
    checkFavoriteStatus,
    pages
  } = useWorkspaceStore();
  
  const [page, setPage] = useState<Page | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [initialContent, setInitialContent] = useState<string>("");
  const [isFavorited, setIsFavorited] = useState(false);
  
  // Debounce refs
  const titleTimeoutRef = useRef<NodeJS.Timeout>();
  const contentTimeoutRef = useRef<NodeJS.Timeout>();

  // Sync with store pages
  useEffect(() => {
    if (pageId && pages.length > 0) {
      const pageFromStore = pages.find(p => p.id === pageId);
      if (pageFromStore) {
        setPage(pageFromStore);
        // Only update title if it's not being edited (simple check)
        // Actually, we should probably trust the store if we are not editing.
        // But for now, let's just update cover_image and icon which are updated via other components.
        // Title is handled locally.
      }
    }
  }, [pageId, pages]);

  useEffect(() => {
    const loadPage = async () => {
      if (pageId) {
        setIsLoading(true);
        try {
          const [pageData, blocks, favorited] = await Promise.all([
            getPage(pageId),
            fetchPageBlocks(pageId),
            checkFavoriteStatus(pageId)
          ]);

          if (pageData) {
            setPage(pageData);
            setTitle(pageData.title);
            setIsFavorited(favorited);
            
            // Find editor content block
            const contentBlock = blocks.find(b => b.type === "editor_content");
            if (contentBlock && contentBlock.content && typeof contentBlock.content.html === 'string') {
              setInitialContent(contentBlock.content.html);
            }
          }
        } catch (error) {
          console.error("Failed to load page:", error);
          toast.error("Failed to load page");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadPage();
  }, [pageId, getPage, fetchPageBlocks, checkFavoriteStatus]);

  const toggleFavorite = async () => {
    if (isFavorited) {
      await removeFavorite(pageId);
      setIsFavorited(false);
      toast.success("Removed from favorites");
    } else {
      await addFavorite(pageId);
      setIsFavorited(true);
      toast.success("Added to favorites");
    }
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = e.target.value;
    setTitle(newTitle);
    
    // Debounce title save
    if (titleTimeoutRef.current) clearTimeout(titleTimeoutRef.current);
    
    titleTimeoutRef.current = setTimeout(async () => {
      try {
        await updatePage(pageId, { title: newTitle });
      } catch (error) {
        console.error("Failed to update title", error);
        toast.error("Failed to save title");
      }
    }, 1000);
  };

  const handleContentChange = useCallback((content: string) => {
    // Debounce content save
    if (contentTimeoutRef.current) clearTimeout(contentTimeoutRef.current);
    
    contentTimeoutRef.current = setTimeout(async () => {
      try {
        await savePageContent(pageId, content);
      } catch (error) {
        console.error("Failed to save content", error);
        toast.error("Failed to save changes");
      }
    }, 2000);
  }, [pageId, savePageContent]);

  const onIconSelect = (icon: string) => {
    updatePage(pageId, { icon });
    setPage(prev => prev ? { ...prev, icon } : null);
  };

  const onRemoveIcon = () => {
    // @ts-ignore
    updatePage(pageId, { icon: null });
    setPage(prev => prev ? { ...prev, icon: undefined } : null);
  };

  const onAddCover = () => {
     coverImage.onOpen();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-muted-foreground">Loading page...</div>
      </div>
    );
  }

  if (!page) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-muted-foreground">Page not found</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto relative">
      <div className="absolute top-4 right-12 z-50 flex items-center gap-x-2">
         <Button
            variant="ghost"
            size="sm"
            onClick={toggleFavorite}
            className={isFavorited ? "text-yellow-500 hover:text-yellow-600" : "text-muted-foreground"}
         >
            <Star className={cn("h-4 w-4", isFavorited && "fill-yellow-500")} />
         </Button>
         <Publish initialData={page} />
      </div>
      <Cover url={page.cover_image} />
      <div className="max-w-4xl mx-auto w-full px-12 py-8">
        <div className="group relative">
          {!!page.icon && (
            <div className="flex items-center gap-x-2 group/icon pt-6">
              <IconPicker onChange={onIconSelect}>
                <p className="text-6xl hover:opacity-75 transition cursor-pointer">
                  {page.icon}
                </p>
              </IconPicker>
              <Button
                onClick={onRemoveIcon}
                className="rounded-full opacity-0 group-hover/icon:opacity-100 transition text-muted-foreground text-xs"
                variant="outline"
                size="icon"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}
          <div className="opacity-0 group-hover:opacity-100 flex items-center gap-x-1 py-4">
            {!page.icon && (
              <IconPicker onChange={onIconSelect} asChild>
                <Button
                  className="text-muted-foreground text-xs"
                  variant="ghost"
                  size="sm"
                >
                  <Smile className="h-4 w-4 mr-2" />
                  Add icon
                </Button>
              </IconPicker>
            )}
            {!page.cover_image && (
              <Button
                onClick={onAddCover}
                className="text-muted-foreground text-xs"
                variant="ghost"
                size="sm"
              >
                <ImageIcon className="h-4 w-4 mr-2" />
                Add cover
              </Button>
            )}
          </div>
          <Input
            value={title}
            onChange={handleTitleChange}
            className="text-4xl font-bold border-none px-0 focus-visible:ring-0 bg-transparent placeholder:text-muted-foreground/50 h-auto py-2"
            placeholder="Untitled"
          />
        </div>
        <div className="mt-4">
          <Editor 
            initialContent={initialContent}
            onChange={handleContentChange}
          />
        </div>
      </div>
    </div>
  );
}
