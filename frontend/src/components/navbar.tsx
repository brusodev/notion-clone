"use client";

import { useWorkspaceStore } from "@/stores/workspace-store";
import { useParams } from "next/navigation";
import { Menu } from "lucide-react";
import { Page } from "@/types";
import { Fragment } from "react";
import { Slash } from "lucide-react";

interface NavbarProps {
  isCollapsed: boolean;
  onResetWidth: () => void;
}

export const Navbar = ({
  isCollapsed,
  onResetWidth
}: NavbarProps) => {
  const params = useParams();
  const { pages } = useWorkspaceStore();
  const pageId = params.pageId as string;

  const getPath = (pageId: string, allPages: Page[]): Page[] => {
    const page = allPages.find(p => p.id === pageId);
    if (!page) return [];
    
    if (page.parent_id) {
      const parentPath = getPath(page.parent_id, allPages);
      return [...parentPath, page];
    }
    
    return [page];
  };

  const path = getPath(pageId, pages);

  return (
    <nav className="bg-background dark:bg-[#1F1F1F] px-3 py-2 w-full flex items-center gap-x-2">
      {isCollapsed && (
        <Menu 
          role="button" 
          onClick={onResetWidth} 
          className="h-6 w-6 text-muted-foreground cursor-pointer hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-sm" 
        />
      )}
      <div className="flex items-center gap-x-1 text-sm">
        {path.map((page, index) => (
          <Fragment key={page.id}>
            {index > 0 && (
              <Slash className="h-4 w-4 text-muted-foreground/50" />
            )}
            <div className="flex items-center gap-x-1 text-muted-foreground hover:text-primary cursor-pointer truncate max-w-[150px]">
              {!!page.icon && <span>{page.icon}</span>}
              <span className="truncate">{page.title}</span>
            </div>
          </Fragment>
        ))}
      </div>
    </nav>
  );
};
