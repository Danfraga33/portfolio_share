import { useState } from "react";
import { ExternalLink } from "lucide-react";

const themes = [
  "Defense",
  "Supply Chain re-development",
  "Commodities",
  "Precious Metals",
  "Semiconductor",
  "Artificial Intelligence",
];

const researchData = {
  Defense: [
    { title: "Q4 2024 Economic Outlook", url: "#", date: "2024-01-15" },
    { title: "Inflation Trends Analysis", url: "#", date: "2024-01-10" },
    { title: "Employment Market Dynamics", url: "#", date: "2024-01-05" },
  ],
  "Emerging Technologies": [
    { title: "AI Investment Landscape 2024", url: "#", date: "2024-01-20" },
    {
      title: "Quantum Computing Market Analysis",
      url: "#",
      date: "2024-01-18",
    },
    { title: "Biotech Innovation Report", url: "#", date: "2024-01-12" },
  ],

  "Innovation Trends": [
    { title: "Technology Adoption Cycles", url: "#", date: "2024-01-23" },
    { title: "Startup Ecosystem Analysis", url: "#", date: "2024-01-07" },
  ],
};

export default function ResearchPage() {
  const [selectedTheme, setSelectedTheme] = useState("Economic Indicators");

  return (
    <div className="bg-background min-h-screen">
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          <h1 className="text-foreground text-2xl font-light tracking-tight">
            Research
          </h1>

          {/* Research Content */}
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {/* Themes List */}
            <div className="space-y-4">
              <h2 className="text-foreground text-lg font-light">Themes</h2>
              <div className="space-y-1">
                {themes.map((theme) => (
                  <button
                    key={theme}
                    onClick={() => setSelectedTheme(theme)}
                    className={`w-full rounded-md px-3 py-2 text-left text-sm transition-colors ${
                      selectedTheme === theme
                        ? "bg-muted text-foreground"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                    }`}
                  >
                    {theme}
                  </button>
                ))}
              </div>
            </div>

            {/* Research Links */}
            <div className="space-y-4 lg:col-span-2">
              <h2 className="text-foreground text-lg font-light">
                Research: {selectedTheme}
              </h2>
              <div className="space-y-3">
                {researchData[selectedTheme as keyof typeof researchData]?.map(
                  (item, index) => (
                    <div
                      key={index}
                      className="border-border hover:bg-muted/50 group rounded-lg border p-4 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <h3 className="text-foreground group-hover:text-primary font-medium transition-colors">
                            {item.title}
                          </h3>
                          <p className="text-muted-foreground text-xs">
                            {item.date}
                          </p>
                        </div>
                        <a
                          href={item.url}
                          className="flex items-center justify-center"
                        >
                          <ExternalLink className="text-muted-foreground group-hover:text-foreground h-4 w-4 transition-colors" />
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
