"use client";

import { usePathname } from "next/navigation";

const titles: Record<string, string> = {
  "/": "Dashboard",
  "/create": "Create Post",
  "/posts": "Posts",
  "/calendar": "Content Calendar",
  "/settings": "Settings",
};

export function Header() {
  const pathname = usePathname();
  const title = titles[pathname] || (pathname.startsWith("/posts/") ? "Post Detail" : "Link Agent");

  return (
    <header className="h-16 border-b border-gray-200 bg-white flex items-center justify-between px-8">
      <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      <div className="flex items-center gap-4">
        <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
          A
        </div>
      </div>
    </header>
  );
}
