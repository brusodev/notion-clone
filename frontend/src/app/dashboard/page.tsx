"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, router]);

  const handleLogout = () => {
    logout();
    router.push("/auth/login");
  };

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container flex h-16 items-center justify-between px-4">
          <h1 className="text-xl font-semibold">Notion Clone</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              Olá, {user.name}
            </span>
            <Button variant="outline" onClick={handleLogout}>
              Sair
            </Button>
          </div>
        </div>
      </header>

      <main className="container px-4 py-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold">Bem-vindo ao Dashboard!</h2>
          <p className="mt-4 text-lg text-muted-foreground">
            O frontend foi configurado com sucesso!
          </p>
          <div className="mt-8 space-y-4">
            <div className="rounded-lg border p-4">
              <h3 className="font-semibold">✅ Setup completo</h3>
              <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                <li>✓ Next.js 14 com TypeScript</li>
                <li>✓ Tailwind CSS configurado</li>
                <li>✓ Zustand para state management</li>
                <li>✓ React Query configurado</li>
                <li>✓ API client com Axios</li>
                <li>✓ Autenticação funcionando</li>
              </ul>
            </div>

            <div className="rounded-lg border p-4">
              <h3 className="font-semibold">🚀 Próximos passos</h3>
              <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                <li>• Implementar sidebar com workspaces</li>
                <li>• Criar sistema de páginas</li>
                <li>• Adicionar editor de blocos</li>
                <li>• Sistema de comentários e tags</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
