"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Page } from "@/types";
import { SidebarItem } from "./SidebarItem";
import { cn } from "@/lib/utils";
import { FileIcon } from "lucide-react";

interface PageListProps {
  pages: Page[];
  level?: number;
}

export const PageList = ({
  pages,
  level = 0
}: PageListProps) => {
  const params = useParams();
  const router = useRouter();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const onExpand = (pageId: string) => {
    setExpanded(prev => ({
      ...prev,
      [pageId]: !prev[pageId]
    }));
  };

  const onRedirect = (pageId: string) => {
    router.push(`/dashboard/${pageId}`);
  };

  if (pages.length === 0) {
    return (
      <div
        style={{ paddingLeft: level ? `${(level * 12) + 25}px` : undefined }}
        className={cn(
          "hidden text-sm font-medium text-muted-foreground/80",
          expanded && "last:block",
          level === 0 && "hidden"
        )}
      >
        No pages inside
      </div>
    );
  }

  return (
    <>
      {pages.map((page) => (
        <div key={page.id}>
          <SidebarItem
            id={page.id}
            onClick={() => onRedirect(page.id)}
            label={page.title}
            icon={FileIcon}
            active={params.pageId === page.id}
            level={level}
            onExpand={() => onExpand(page.id)}
            expanded={expanded[page.id]}
            page={page}
          />
          {expanded[page.id] && (
            <PageList
              pages={page.children || []}
              level={level + 1}
            />
          )}
        </div>
      ))}
    </>
  );
};
