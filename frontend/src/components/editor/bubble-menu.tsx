"use client";

import { BubbleMenu, BubbleMenuProps, isNodeSelection } from "@tiptap/react";
import { 
  Bold, 
  Italic, 
  Strikethrough, 
  Code, 
  Link as LinkIcon
} from "lucide-react";
import { useState, useCallback } from "react";

import { cn } from "@/lib/utils";

export interface EditorBubbleMenuProps extends Omit<BubbleMenuProps, "children"> {
  className?: string;
}

export const EditorBubbleMenu = ({ editor, className, ...props }: EditorBubbleMenuProps) => {
  const [isLinkOpen, setIsLinkOpen] = useState(false);
  const [linkUrl, setLinkUrl] = useState("");

  const onSetLink = useCallback(() => {
    if (!editor) return;
    
    const previousUrl = editor.getAttributes("link").href;
    setLinkUrl(previousUrl || "");
    setIsLinkOpen(true);
  }, [editor]);

  const onLinkSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!editor) return;

    if (linkUrl === "") {
      editor.chain().focus().extendMarkRange("link").toggleLink({ href: "" }).run();
    } else {
      editor.chain().focus().extendMarkRange("link").toggleLink({ href: linkUrl }).run();
    }
    setIsLinkOpen(false);
  }, [editor, linkUrl]);

  if (!editor) return null;

  return (
    <BubbleMenu
      editor={editor}
      tippyOptions={{ duration: 100 }}
      shouldShow={({ editor, view, state, from, to }) => {
        const { doc, selection } = state;
        const { empty } = selection;

        // Don't show on empty selection
        if (empty) return false;

        // Don't show on image selection
        if (isNodeSelection(selection)) return false;

        // Don't show if link input is open
        if (isLinkOpen) return true;

        return true;
      }}
      className={cn(
        "flex w-fit divide-x divide-neutral-200 dark:divide-neutral-700 rounded-md border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 shadow-xl overflow-hidden",
        className
      )}
      {...props}
    >
      {isLinkOpen ? (
        <form onSubmit={onLinkSubmit} className="flex items-center p-1">
          <input
            type="url"
            placeholder="https://"
            className="flex-1 bg-transparent outline-none text-sm px-2 min-w-[200px] text-neutral-600 dark:text-neutral-300 placeholder:text-neutral-400"
            value={linkUrl}
            onChange={(e) => setLinkUrl(e.target.value)}
            autoFocus
          />
          <button
            type="button"
            onClick={() => setIsLinkOpen(false)}
            className="p-1 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-sm text-neutral-500"
          >
            <span className="text-xs">Esc</span>
          </button>
        </form>
      ) : (
        <div className="flex items-center">
          <button
            onClick={() => editor.chain().focus().toggleBold().run()}
            className={cn(
              "p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 text-neutral-500",
              editor.isActive("bold") && "text-blue-500 bg-blue-50 dark:bg-blue-900/20"
            )}
          >
            <Bold className="w-4 h-4" />
          </button>
          <button
            onClick={() => editor.chain().focus().toggleItalic().run()}
            className={cn(
              "p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 text-neutral-500",
              editor.isActive("italic") && "text-blue-500 bg-blue-50 dark:bg-blue-900/20"
            )}
          >
            <Italic className="w-4 h-4" />
          </button>
          <button
            onClick={() => editor.chain().focus().toggleStrike().run()}
            className={cn(
              "p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 text-neutral-500",
              editor.isActive("strike") && "text-blue-500 bg-blue-50 dark:bg-blue-900/20"
            )}
          >
            <Strikethrough className="w-4 h-4" />
          </button>
          <button
            onClick={() => editor.chain().focus().toggleCode().run()}
            className={cn(
              "p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 text-neutral-500",
              editor.isActive("code") && "text-blue-500 bg-blue-50 dark:bg-blue-900/20"
            )}
          >
            <Code className="w-4 h-4" />
          </button>
          <button
            onClick={onSetLink}
            className={cn(
              "p-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 text-neutral-500",
              editor.isActive("link") && "text-blue-500 bg-blue-50 dark:bg-blue-900/20"
            )}
          >
            <LinkIcon className="w-4 h-4" />
          </button>
        </div>
      )}
    </BubbleMenu>
  );
};
