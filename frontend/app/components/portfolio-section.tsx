const portfolioData = {
  funds: [
    {
      name: "Economic",
      description: "Macro-economic focused investments",
    },
    {
      name: "Emerging Tech",
      description: "Technology and innovation investments",
    },
  ],
  themes: {
    Economic: ["Commodities", "Defense", "Supply Chain re-alignment"],
    "Emerging Tech": [
      "Artificial Intelligence",
      "Quantum Computing",
      "Semiconductor",
    ],
  },
  investments: {
    Commodities: [
      { name: "VanEck Gold Miners ETF", ticker: "GDX.AU" },
      { name: "BetaShares Gold Bullion ETF", ticker: "QAU.AU" },
      { name: "ETFS Physical Gold", ticker: "GOLD.AU" },
      { name: "ETFS Physical Silver", ticker: "ETPMAG.AU" },
      { name: "First Majestic Silver Corp.", ticker: "AG" },
      { name: "Global X Uranium ETF", ticker: "URA" },
      { name: "Global X Lithium & Battery Tech ETF", ticker: "LIT" },
      { name: "Solomon Gold Ltd", ticker: "SLM" },
      { name: "Heavy Metals Limited", ticker: "HVY" },
      { name: "iShares S&P GSCI Commodity Indexed Trust", ticker: "GSG" },
    ],
    Defense: [
      { name: "RTX Corporation", ticker: "RTX" },
      { name: "Palantir Technologies Inc.", ticker: "PLTR" },
    ],
    Supply_Chain: [
      { name: "Rockwell Automation, Inc.", ticker: "ROK" },
      { name: "Symbotic Inc.", ticker: "SYM" },
    ],
    AI: [
      { name: "NVIDIA Corporation", ticker: "NVDA" },
      { name: "Snowflake Inc.", ticker: "SNOW" },
      { name: "ServiceNow, Inc.", ticker: "NOW" },
      { name: "InMode Ltd.", ticker: "INMD" },
    ],
    Semiconductor: [
      { name: "Taiwan Semiconductor Manufacturing Co. Ltd.", ticker: "TSM" },
      { name: "ASML Holding N.V.", ticker: "ASML" },
    ],
  },
};
const themeKeyMap = {
  Commodities: "Commodities",
  Defense: "Defense",
  "Supply Chain re-alignment": "Supply_Chain",
  "Artificial Intelligence": "AI",
  "Quantum Computing": "Quantum_Computing",
  Semiconductor: "Semiconductor",
};

import * as React from "react";

export function PortfolioSection() {
  const [activeFund, setActiveFund] = React.useState("Economic");

  const activeThemes =
    portfolioData.themes[activeFund as keyof typeof portfolioData.themes];

  const activeInvestments = activeThemes.reduce(
    (acc, theme) => {
      const themeKey = themeKeyMap[
        theme as keyof typeof themeKeyMap
      ] as keyof typeof portfolioData.investments;
      if (portfolioData.investments[themeKey]) {
        acc[theme] = portfolioData.investments[themeKey];
      }
      return acc;
    },
    {} as Record<string, { name: string; ticker: string }[]>,
  );

  return (
    <section className="space-y-8">
      <h2 className="text-foreground text-xl font-light">Portfolio</h2>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="space-y-4">
          <h3 className="text-foreground border-border border-b pb-2 text-lg font-light">
            Funds
          </h3>
          <div className="space-y-4">
            {portfolioData.funds.map((fund, index) => (
              <div key={index} className="space-y-2">
                <button
                  onClick={() => setActiveFund(fund.name)}
                  className={`text-foreground font-medium transition-all ${activeFund === fund.name ? "underline underline-offset-4" : "opacity-70 hover:opacity-100"} `}
                  style={{
                    cursor: "pointer",
                    background: "none",
                    border: "none",
                    padding: 0,
                  }}
                  aria-current={activeFund === fund.name ? "page" : undefined}
                >
                  {fund.name}
                </button>
                <p className="text-muted-foreground text-sm">
                  {fund.description}
                </p>
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-4">
          <h3 className="text-foreground border-border border-b pb-2 text-lg font-light">
            Themes
          </h3>
          <ul className="space-y-2">
            {activeThemes.map((theme, index) => (
              <li key={index} className="text-muted-foreground text-sm">
                {theme}
              </li>
            ))}
          </ul>
        </div>
        <div className="space-y-4">
          <h3 className="text-foreground border-border border-b pb-2 text-lg font-light">
            Investments
          </h3>
          <div className="space-y-6">
            {Object.entries(activeInvestments).map(([theme, investments]) => (
              <div key={theme} className="space-y-3">
                <h4 className="text-foreground text-sm font-medium">{theme}</h4>
                <ul className="space-y-1">
                  {investments.map((investment, index) => (
                    <li
                      key={index}
                      className="text-muted-foreground flex items-center justify-between text-sm"
                    >
                      <span>{investment.name}</span>
                      <span className="text-foreground/60 ml-2 font-mono text-xs">
                        {investment.ticker}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
