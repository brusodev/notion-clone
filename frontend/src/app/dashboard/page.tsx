"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { Button } from "@/components/ui/button";
import { PlusCircle, FileText } from "lucide-react";
import { toast } from "sonner";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { createPage, pages } = useWorkspaceStore();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

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

  if (!user) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col items-center justify-center space-y-4">
      <div className="max-w-3xl space-y-4 text-center">
        <h2 className="text-3xl font-bold">
          Welcome to {user.name}&apos;s Notion
        </h2>
        <p className="text-muted-foreground text-lg">
          This is your personal workspace. You can create pages, write notes, and organize your life.
        </p>
        
        <Button onClick={handleCreatePage}>
          <PlusCircle className="h-4 w-4 mr-2" />
          Create a page
        </Button>
      </div>

      {pages.length > 0 && (
        <div className="w-full max-w-3xl mt-8">
          <h3 className="text-sm font-medium text-muted-foreground mb-4">Recent Pages</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {pages.slice(0, 6).map((page) => (
              <div 
                key={page.id}
                onClick={() => router.push(`/dashboard/${page.id}`)}
                className="group flex flex-col items-center justify-center border rounded-lg p-4 hover:bg-secondary/50 cursor-pointer transition-colors aspect-video"
              >
                <FileText className="h-8 w-8 text-muted-foreground mb-2 group-hover:text-primary transition-colors" />
                <span className="font-medium truncate w-full text-center">
                  {page.title}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
