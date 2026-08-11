import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ATLAS - Intelligent Learning & University Program Recommendations",
  description:
    "ATLAS is an intelligent learning platform for secondary students in Ghana. Practise challenges, study lessons, track progress, and explore university programme recommendations.",
  keywords: ["ATLAS", "education", "learning", "career guidance", "WASSCE", "university recommendations", "Ghana", "SHS"],
  other: {
    "color-scheme": "light only",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#F8FAFC" },
    { media: "(prefers-color-scheme: dark)", color: "#F8FAFC" },
  ],
  colorScheme: "light",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light" style={{ colorScheme: "light" }} suppressHydrationWarning>
      <body className={`${inter.className} bg-[#F8FAFC] text-[#1E293B]`} suppressHydrationWarning>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
