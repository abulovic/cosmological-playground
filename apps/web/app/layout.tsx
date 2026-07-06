import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Cosmology Lens",
  description: "Evidence-bearing cosmology analysis for text",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
