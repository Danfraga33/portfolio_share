import type { MetaFunction } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";
import { MacroChart } from "~/components/macro-chart";
import { PortfolioSection } from "~/components/portfolio-section";

export const loader = async () => {
  const base = process.env.PUBLIC_API_URL;
  if (!base) throw new Error("Missing PUBLIC_API_URL env var");

  const res = await fetch(`${base}/api/macro-compass`);
  if (!res.ok) throw new Error(await res.text());
  const obj = await res.json();

  // Transform as before (e.g. map to array)
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
