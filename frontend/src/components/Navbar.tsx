"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();
  const isActive = (p: string) =>
    pathname === p ? "text-green-600 font-semibold" : "text-gray-600";

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200">
      <div className="max-w-2xl mx-auto px-6">
        <div className="flex items-center justify-between h-14">
          <Link href="/" className={`flex flex-col items-center ${isActive("/")}`}>
            <span>🏠</span>
            <span className="text-xs">Hem</span>
          </Link>
          <Link
            href="/kostschema"
            className={`flex flex-col items-center ${isActive("/kostschema")}`}
          >
            <span>📄</span>
            <span className="text-xs">Kostschema</span>
          </Link>
          <Link
            href="/foods"
            className={`flex flex-col items-center ${isActive("/foods")}`}
          >
            <span>🥑</span>
            <span className="text-xs">Dagbok</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}
