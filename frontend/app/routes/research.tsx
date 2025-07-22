import { useState } from "react";
import { ExternalLink } from "lucide-react";

const themes = [
  "Defense",
  "Supply Chain re-development",
  "Commodities",
  "Semiconductor",
  "Artificial Intelligence",
  "Strategy",
];

const researchData = {
  Defense: [
    {
      title: "The New Defense Spending Supercycle (2025 Outlook)",
      url: "https://danfraga33.wixsite.com/my-site-5/post/the-new-defense-spending-supercycle-2025-outlook",
      date: "2025-05-15",
    },
  ],
  Commodities: [
    {
      title: "Commodities Supercycle: A Secular Bull Market Thesis",
      url: "https://danfraga33.wixsite.com/my-site-5/post/commodities-supercycle-a-secular-bull-market-thesis",
      date: "2025-01-02",
    },
  ],
  "Supply Chain": [
    {
      title:
        "The Next Industrial Supercycle: My 2025 Investment Thesis on Supply Chain Re-Architecture",
      url: "https://danfraga33.wixsite.com/my-site-5/post/the-next-industrial-supercycle-my-2025-investment-thesis-on-supply-chain-re-architecture",
      date: "2025-04-12",
    },
  ],

  Strategy: [
    {
      title:
        "The Portfolio In Motion: A Macro Compass, Two Funds, Three-Stock Themes",
      url: "https://danfraga33.wixsite.com/my-site-5/post/the-portfolio-in-motion-a-macro-compass-two-funds-three-stock-themes",
      date: "2025-01-23",
    },
    {
      title:
        "The Top-Down Investor: My High-Leverage Investment Themes for the Next Decade",
      url: "https://danfraga33.wixsite.com/my-site-5/post/the-top-down-investor-my-high-leverage-investment-themes-for-the-next-decade",
      date: "2025-01-01",
    },
  ],
};

export default function ResearchPage() {
  const [selectedTheme, setSelectedTheme] = useState("Economic Indicators");

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          <h1 className="text-2xl font-light tracking-tight text-foreground">
            Research
          </h1>

          {/* Research Content */}
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {/* Themes List */}
            <div className="space-y-4">
              <h2 className="text-lg font-light text-foreground">Themes</h2>
              <div className="space-y-1">
                {themes.map((theme) => (
                  <button
                    key={theme}
                    onClick={() => setSelectedTheme(theme)}
                    className={`w-full rounded-md px-3 py-2 text-left text-sm transition-colors ${
                      selectedTheme === theme
                        ? "bg-muted text-foreground"
                        : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                    }`}
                  >
                    {theme}
                  </button>
                ))}
              </div>
            </div>

            {/* Research Links */}
            <div className="space-y-4 lg:col-span-2">
              <h2 className="text-lg font-light text-foreground">
                Research: {selectedTheme}
              </h2>
              <div className="space-y-3">
                {researchData[selectedTheme as keyof typeof researchData]?.map(
                  (item, index) => (
                    <div
                      key={index}
                      className="group rounded-lg border border-border p-4 transition-colors hover:bg-muted/50"
                    >
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <h3 className="font-medium text-foreground transition-colors group-hover:text-primary">
                            {item.title}
                          </h3>
                          <p className="text-xs text-muted-foreground">
                            {item.date}
                          </p>
                        </div>
                        <a
                          href={item.url}
                          className="flex items-center justify-center"
                        >
                          <ExternalLink className="h-4 w-4 text-muted-foreground transition-colors group-hover:text-foreground" />
                        </a>
                      </div>
                    </div>
                  ),
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
