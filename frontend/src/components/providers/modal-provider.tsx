"use client";

import { useEffect, useState } from "react";
import { CoverImageModal } from "@/components/modals/cover-image-modal";
import { useCoverImage } from "@/hooks/use-cover-image";

export const ModalProvider = () => {
  const [isMounted, setIsMounted] = useState(false);
  const coverImage = useCoverImage();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  return (
    <>
      <CoverImageModal 
        isOpen={coverImage.isOpen} 
        onClose={coverImage.onClose} 
      />
    </>
  );
};
