import type { MetaFunction } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";
import { MacroChart } from "~/components/macro-chart";
import { PortfolioSection } from "~/components/portfolio-section";

export const loader = async () => {
  const res = await fetch("http://localhost:8000/api/macro-compass");
  if (!res.ok) throw new Error(await res.text());
  const obj = await res.json(); // { [date: string]: { composite_score: number; … } }

  // Turn into array of { date, value }
  const data = Object.entries(obj).map(([date, row]) => ({
    date,
    value: row.composite_score,
  }));

  return { chartData: data };
};

export const meta: MetaFunction = () => {
  return [
    { title: "Portfolio " },
    { name: "description", content: "Welcome to Remix!" },
  ];
};

export default function Index() {
  const { chartData } = useLoaderData<typeof loader>();
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-12">
          <section className="space-y-4">
            <h2 className="text-2xl font-light text-foreground">
              Macro Compass
            </h2>
            <MacroChart chartData={chartData} />
          </section>

          <PortfolioSection />
        </div>
      </main>
    </div>
  );
}
