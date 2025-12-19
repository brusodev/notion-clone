"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { useParams } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Upload, Link as LinkIcon, Image as ImageIcon, Loader2 } from "lucide-react";
import Image from "next/image";

interface CoverImageModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PRESETS = [
  "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1200&h=400&fit=crop",
  "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200&h=400&fit=crop",
  "https://images.unsplash.com/photo-1532274402911-5a369e4c4bb5?w=1200&h=400&fit=crop",
  "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1200&h=400&fit=crop"
];

export const CoverImageModal = ({
  isOpen,
  onClose
}: CoverImageModalProps) => {
  const params = useParams();
  const { updatePage, uploadFile, currentWorkspace } = useWorkspaceStore();
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [url, setUrl] = useState("");
  const [activeTab, setActiveTab] = useState<"gallery" | "upload" | "link">("gallery");

  const onUpload = async (selectedFile: File) => {
    if (!currentWorkspace) return;
    
    setIsSubmitting(true);
    try {
      const storageUrl = await uploadFile(selectedFile, currentWorkspace.id, params.pageId as string);
      if (storageUrl) {
        await updatePage(params.pageId as string, { cover_image: storageUrl });
        onClose();
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const onLinkSubmit = async () => {
    if (!url) return;
    setIsSubmitting(true);
    try {
      await updatePage(params.pageId as string, { cover_image: url });
      onClose();
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const onPresetSelect = async (presetUrl: string) => {
    setIsSubmitting(true);
    try {
      await updatePage(params.pageId as string, { cover_image: presetUrl });
      onClose();
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-center font-bold">Cover Image</DialogTitle>
        </DialogHeader>
        
        <div className="flex items-center justify-center gap-x-2 mb-4">
            <Button 
                variant={activeTab === "gallery" ? "default" : "outline"} 
                size="sm"
                onClick={() => setActiveTab("gallery")}
            >
                <ImageIcon className="h-4 w-4 mr-2" />
                Gallery
            </Button>
            <Button 
                variant={activeTab === "upload" ? "default" : "outline"} 
                size="sm"
                onClick={() => setActiveTab("upload")}
            >
                <Upload className="h-4 w-4 mr-2" />
                Upload
            </Button>
            <Button 
                variant={activeTab === "link" ? "default" : "outline"} 
                size="sm"
                onClick={() => setActiveTab("link")}
            >
                <LinkIcon className="h-4 w-4 mr-2" />
                Link
            </Button>
        </div>

        {activeTab === "gallery" && (
            <div className="grid grid-cols-2 gap-2">
                {PRESETS.map((preset, index) => (
                    <div 
                        key={index} 
                        className="relative h-24 w-full cursor-pointer hover:opacity-75 transition rounded-md overflow-hidden border"
                        onClick={() => onPresetSelect(preset)}
                    >
                        <Image src={preset} fill alt="Preset" className="object-cover" />
                    </div>
                ))}
            </div>
        )}

        {activeTab === "upload" && (
            <div className="flex flex-col items-center justify-center gap-y-4 p-4 border-2 border-dashed rounded-md">
                <Input 
                    type="file" 
                    accept="image/*"
                    disabled={isSubmitting}
                    onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) onUpload(file);
                    }}
                    className="cursor-pointer"
                />
                <p className="text-xs text-muted-foreground">
                    Max file size: 5MB
                </p>
                {isSubmitting && <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />}
            </div>
        )}

        {activeTab === "link" && (
            <div className="flex gap-x-2">
                <Input 
                    placeholder="Paste image link..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={isSubmitting}
                />
                <Button onClick={onLinkSubmit} disabled={isSubmitting}>
                    Submit
                </Button>
            </div>
        )}

      </DialogContent>
    </Dialog>
  );
};
