"use client"

import { cn, buildPageTree } from "@/lib/utils"
import { 
  ChevronsLeft, 
  Menu, 
  Plus, 
  Search, 
  Settings,
  Trash
} from "lucide-react"
import { useRouter } from "next/navigation"
import React, { ElementRef, useEffect, useRef, useState } from "react"
import { useWorkspaceStore } from "@/stores/workspace-store"
import { useSearch } from "@/hooks/use-search"
import { toast } from "sonner"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover"
import { ChevronsUpDown } from "lucide-react"

import { PageList } from "./PageList"
import { TrashBox } from "@/components/trash-box"
import { Navbar } from "@/components/navbar"

export const Sidebar = () => {
  const router = useRouter();
  const search = useSearch();
  const { 
    workspaces,
    currentWorkspace, 
    pages, 
    favorites,
    fetchWorkspaces, 
    fetchFavorites,
    selectWorkspace,
    createPage 
  } = useWorkspaceStore();

  // Build page tree
  const rootPages = buildPageTree(pages);

  const isMobile = false; // TODO: Implement mobile detection
  // const isResizingRef = useRef(false);
  const sidebarRef = useRef<ElementRef<"aside">>(null);
  const navbarRef = useRef<ElementRef<"div">>(null);
  const [isResetting, setIsResetting] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(isMobile);

  useEffect(() => {
    fetchWorkspaces();
    fetchFavorites();
  }, [fetchWorkspaces, fetchFavorites]);

  const handleCreatePage = async () => {
    const promise = createPage("Untitled");
    
    toast.promise(promise, {
      loading: "Creating a new page...",
      success: "New page created!",
      error: "Failed to create a new page."
    });

    const newPage = await promise;
    if (newPage) {
      router.push(`/dashboard/${newPage.id}`);
    }
  };

  const resetWidth = () => {
    if (sidebarRef.current && navbarRef.current) {
      setIsCollapsed(false);
      setIsResetting(true);

      sidebarRef.current.style.width = isMobile ? "100%" : "240px";
      navbarRef.current.style.setProperty(
        "width",
        isMobile ? "0" : "calc(100% - 240px)"
      );
      navbarRef.current.style.setProperty(
        "left",
        isMobile ? "100%" : "240px"
      );
      setTimeout(() => setIsResetting(false), 300);
    }
  };

  const collapse = () => {
    if (sidebarRef.current && navbarRef.current) {
      setIsCollapsed(true);
      setIsResetting(true);

      sidebarRef.current.style.width = "0";
      navbarRef.current.style.setProperty("width", "100%");
      navbarRef.current.style.setProperty("left", "0");
      setTimeout(() => setIsResetting(false), 300);
    }
  }

  return (
    <>
      <aside
        ref={sidebarRef}
        className={cn(
          "group/sidebar h-full bg-secondary overflow-y-auto relative flex w-60 flex-col z-40",
          isResetting && "transition-all ease-in-out duration-300",
          isMobile && "w-0"
        )}
      >
        <div
          role="button"
          onClick={collapse}
          className={cn(
            "h-6 w-6 text-muted-foreground rounded-sm hover:bg-neutral-300 dark:hover:bg-neutral-600 absolute top-3 right-2 opacity-0 group-hover/sidebar:opacity-100 transition",
            isMobile && "opacity-100"
          )}
        >
          <ChevronsLeft className="h-6 w-6" />
        </div>
        
        <div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div role="button" className="flex items-center text-sm p-3 w-full hover:bg-primary/5 font-medium cursor-pointer">
                <div className="flex items-center gap-x-2 w-full">
                  <div className="h-5 w-5 bg-secondary-foreground/10 rounded-sm flex items-center justify-center">
                    <span className="text-xs font-bold">
                      {currentWorkspace?.name?.[0]?.toUpperCase() || "W"}
                    </span>
                  </div>
                  <span className="truncate font-medium">
                    {currentWorkspace?.name || "Select Workspace"}
                  </span>
                  <ChevronsUpDown className="ml-auto h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className="w-60"
              align="start"
              alignOffset={11}
              forceMount
            >
              <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
                Workspaces
              </DropdownMenuLabel>
              {workspaces.map((workspace) => (
                <DropdownMenuItem
                  key={workspace.id}
                  onClick={() => selectWorkspace(workspace.id)}
                  className="cursor-pointer"
                >
                  <div className="flex items-center gap-x-2">
                    <div className="h-5 w-5 bg-secondary-foreground/10 rounded-sm flex items-center justify-center">
                      <span className="text-xs font-bold">
                        {workspace.name[0].toUpperCase()}
                      </span>
                    </div>
                    <span className="truncate">{workspace.name}</span>
                  </div>
                  {currentWorkspace?.id === workspace.id && (
                    <div className="ml-auto h-2 w-2 rounded-full bg-primary" />
                  )}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer text-muted-foreground">
                <Plus className="h-4 w-4 mr-2" />
                Create Workspace
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <div className="mt-4">
            <div 
              onClick={search.onOpen}
              className="flex items-center text-sm p-3 w-full hover:bg-primary/5 cursor-pointer text-muted-foreground font-medium"
            >
              <Search className="h-4 w-4 mr-2" />
              <span>Search</span>
              <span className="ml-auto text-xs text-muted-foreground/50">
                Ctrl K
              </span>
            </div>
            <div className="flex items-center text-sm p-3 w-full hover:bg-primary/5 cursor-pointer text-muted-foreground font-medium">
              <Settings className="h-4 w-4 mr-2" />
              <span>Settings</span>
            </div>
            <div 
              onClick={handleCreatePage}
              className="flex items-center text-sm p-3 w-full hover:bg-primary/5 cursor-pointer text-muted-foreground font-medium"
            >
              <Plus className="h-4 w-4 mr-2" />
              <span>New Page</span>
            </div>
            <Popover>
              <PopoverTrigger className="w-full mt-4">
                <div className="flex items-center text-sm p-3 w-full hover:bg-primary/5 cursor-pointer text-muted-foreground font-medium">
                  <Trash className="h-4 w-4 mr-2" />
                  <span>Trash</span>
                </div>
              </PopoverTrigger>
              <PopoverContent
                className="p-0 w-72"
                side={isMobile ? "bottom" : "right"}
              >
                <TrashBox />
              </PopoverContent>
            </Popover>
          </div>
        </div>
        
        <div className="mt-4">
           {favorites.length > 0 && (
             <div className="px-3 py-2">
                <h3 className="text-xs font-medium text-muted-foreground mb-2 px-2">Favorites</h3>
                <PageList pages={favorites} />
             </div>
           )}
           <div className="px-3 py-2">
              <h3 className="text-xs font-medium text-muted-foreground mb-2 px-2">Private</h3>
              {rootPages.length === 0 ? (
                <p className="text-xs text-muted-foreground px-2">No pages inside</p>
              ) : (
                <PageList pages={rootPages} />
              )}
           </div>
        </div>

        <div
          className="opacity-0 group-hover/sidebar:opacity-100 transition cursor-ew-resize absolute h-full w-1 bg-primary/10 right-0 top-0"
        />
      </aside>
      
      <div
        ref={navbarRef}
        className={cn(
          "absolute top-0 z-30 left-60 w-[calc(100%-240px)]",
          isResetting && "transition-all ease-in-out duration-300",
          isMobile && "left-0 w-full"
        )}
      >
        <Navbar
          isCollapsed={isCollapsed}
          onResetWidth={resetWidth}
        />
      </div>
    </>
  )
}
