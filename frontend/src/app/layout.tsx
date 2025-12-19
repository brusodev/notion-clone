import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import "tippy.js/dist/tippy.css";
import { Providers } from "@/components/providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Notion Clone",
  description: "A modern Notion clone built with Next.js and FastAPI",
  icons: {
    icon: [
      {
        url: "/favicon.svg",
        href: "/favicon.svg",
      }
    ]
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
