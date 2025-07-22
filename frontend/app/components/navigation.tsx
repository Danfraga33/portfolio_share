import { Link, useLocation } from "@remix-run/react";
import { ThemeToggle } from "./theme-toggle";

export function Navigation() {
  const { pathname } = useLocation();

  const menuItems = [
    { name: "Macro Compass & Portfolio", href: "/" },
    { name: "Research", href: "/research" },
  ];

  return (
    <header className="border-border bg-background/95 supports-[backdrop-filter]:bg-background/60 sticky top-0 z-40 border-b backdrop-blur">
      <div className="container mx-auto px-4">
        <nav className="flex h-16 items-center justify-center">
          <div className="flex items-center space-x-8">
            {menuItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={`hover:text-foreground/80 text-sm font-light transition-colors ${
                  pathname === item.href
                    ? "text-foreground border-foreground border-b-2 pb-1"
                    : "text-muted-foreground"
                }`}
              >
                {item.name}
              </Link>
            ))}
            <ThemeToggle />
          </div>
        </nav>
      </div>
    </header>
  );
}
