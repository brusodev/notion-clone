// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  password_confirm: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// Workspace types
export interface Workspace {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  is_personal: boolean;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: "owner" | "admin" | "editor" | "viewer";
  user: User;
  joined_at: string;
}

// Page types
export interface Page {
  id: string;
  workspace_id: string;
  title: string;
  icon?: string;
  cover_image?: string;
  parent_id?: string;
  is_archived: boolean;
  is_public: boolean;
  public_slug?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  children?: Page[];
}

// Block types
export type BlockType =
  | "paragraph"
  | "heading_1"
  | "heading_2"
  | "heading_3"
  | "bulleted_list"
  | "numbered_list"
  | "code"
  | "quote"
  | "divider"
  | "editor_content";

export interface Block {
  id: string;
  page_id: string;
  type: BlockType;
  content: Record<string, unknown>;
  parent_id?: string;
  position: number;
  created_at: string;
  updated_at: string;
}

// Comment types
export interface Comment {
  id: string;
  page_id: string;
  block_id?: string;
  user_id: string;
  content: string;
  is_deleted: boolean;
  user: User;
  created_at: string;
  updated_at: string;
}

// Tag types
export interface Tag {
  id: string;
  workspace_id: string;
  name: string;
  color: string;
  created_at: string;
  page_count?: number;
}

// Favorite types
export interface Favorite {
  id: string;
  user_id: string;
  page_id: string;
  page: Page;
  created_at: string;
}

// Version types
export interface PageVersion {
  id: string;
  page_id: string;
  version_number: number;
  title: string;
  snapshot: Record<string, unknown>;
  created_by: string;
  created_at: string;
  user: User;
}

// Search types
export interface SearchResult {
  page_id: string;
  page_title: string;
  block_id?: string;
  block_content?: string;
  rank: number;
}

// API Response types
export interface ApiError {
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
