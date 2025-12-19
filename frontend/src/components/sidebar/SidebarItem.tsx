"use client";

import { 
  ChevronDown, 
  ChevronRight, 
  FileIcon, 
  MoreHorizontal,
  Plus,
  Trash,
  Copy
} from "lucide-react";
import { useRouter, useParams } from "next/navigation";
import { toast } from "sonner";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { cn } from "@/lib/utils";
import { Page } from "@/types";
import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface SidebarItemProps {
  id: string;
  label: string;
  active?: boolean;
  expanded?: boolean;
  level?: number;
  onExpand?: () => void;
  icon?: React.ElementType;
  page?: Page;
}

export const SidebarItem = ({
  id,
  label,
  active,
  expanded,
  level = 0,
  onExpand,
  icon: Icon = FileIcon,
  page,
}: SidebarItemProps) => {
  const router = useRouter();
  const params = useParams();
  const { createPage, archivePage, duplicatePage } = useWorkspaceStore();

  // Use children from page object if available (from buildPageTree)
  const hasChildren = page?.children && page.children.length > 0;

  const handleExpand = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    event.stopPropagation();
    onExpand?.();
  };

  const onClick = () => {
    router.push(`/dashboard/${id}`);
  };

  const onDuplicate = async (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    event.stopPropagation();
    if (!id) return;
    
    const promise = duplicatePage(id);
    
    toast.promise(promise, {
      loading: "Duplicating page...",
      success: "Page duplicated!",
      error: "Failed to duplicate page."
    });
  };

  const onArchive = async (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    event.stopPropagation();
    if (!id) return;
    
    const promise = archivePage(id);
    
    toast.promise(promise, {
      loading: "Moving to trash...",
      success: "Page moved to trash!",
      error: "Failed to archive page."
    });

    try {
      await promise;
      if (params?.pageId === id) {
        router.push("/dashboard");
      }
    } catch (error) {
      // Error handled by toast
    }
  };

  const onCreateChild = async (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    event.stopPropagation();
    if (!id) return;
    
    const promise = createPage("Untitled", id);
    
    toast.promise(promise, {
      loading: "Creating a new page...",
      success: "New page created!",
      error: "Failed to create a new page."
    });

    const newPage = await promise;
    if (newPage) {
      if (!expanded) onExpand?.();
      router.push(`/dashboard/${newPage.id}`);
    }
  };

  const ChevronIcon = expanded ? ChevronDown : ChevronRight;

  return (
    <>
      <div
        onClick={onClick}
        style={{ 
          paddingLeft: level ? `${(level * 12) + 12}px` : "12px"
        }}
        className={cn(
          "group min-h-[27px] text-sm py-1 pr-3 w-full hover:bg-primary/5 flex items-center text-muted-foreground font-medium cursor-pointer",
          active && "bg-primary/5 text-primary"
        )}
      >
        <div
          role="button"
          className="h-full rounded-sm hover:bg-neutral-300 dark:hover:bg-neutral-600 mr-1"
          onClick={handleExpand}
        >
          <ChevronIcon
            className={cn(
              "h-4 w-4 shrink-0 text-muted-foreground/50",
              hasChildren ? "opacity-100" : "opacity-0"
            )}
          />
        </div>
        
        {page?.icon ? (
          <span className="shrink-0 mr-2 text-[18px]">{page.icon}</span>
        ) : (
          <Icon className="shrink-0 h-[18px] w-[18px] mr-2 text-muted-foreground" />
        )}
        
        <span className="truncate">
          {label}
        </span>

        {!!id && (
          <div className="ml-auto flex items-center gap-x-2">
            <DropdownMenu>
              <DropdownMenuTrigger
                onClick={(e) => e.stopPropagation()}
                asChild
              >
                <div
                  role="button"
                  className="opacity-0 group-hover:opacity-100 h-full ml-auto rounded-sm hover:bg-neutral-300 dark:hover:bg-neutral-600"
                >
                  <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-48"
                align="start"
                side="right"
                forceMount
              >
                <DropdownMenuItem onClick={onArchive}>
                  <Trash className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onDuplicate}>
                  <Copy className="h-4 w-4 mr-2" />
                  Duplicate
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <div className="text-xs text-muted-foreground p-2">
                  Last edited by: {page?.created_by}
                </div>
              </DropdownMenuContent>
            </DropdownMenu>
            <div
              role="button"
              onClick={onCreateChild}
              className="opacity-0 group-hover:opacity-100 h-full ml-auto rounded-sm hover:bg-neutral-300 dark:hover:bg-neutral-600"
            >
              <Plus className="h-4 w-4 text-muted-foreground" />
            </div>
          </div>
        )}
      </div>
    </>
  );
};
