import type { LoaderFunctionArgs, MetaFunction } from "@remix-run/node";
import { Await, defer, json, useLoaderData } from "@remix-run/react";
import { Suspense } from "react";
import { ChartLoader } from "~/components/chartLoader";
import { MacroChart } from "~/components/macro-chart";
import { PortfolioSection } from "~/components/portfolio-section";

export const loader = async ({ request }: LoaderFunctionArgs) => {
  const base = process.env.PUBLIC_API_URL;
  if (!base) {
    throw json({ message: "Missing PUBLIC_API_URL env var" }, { status: 500 });
  }

  // Kick off the fetch but don’t await it
  const chartPromise = fetch(`${base}/api/macro-compass`)
    .then((res) => {
      if (!res.ok) throw new Response(res.statusText, { status: res.status });
      return res.json();
    })
    .then((obj: Record<string, { composite_score: number }>) =>
      Object.entries(obj).map(([date, row]) => ({
        date,
        value: row.composite_score,
      })),
    );

  return defer({
    chartData: chartPromise,
  });
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
            <Suspense fallback={<ChartLoader />}>
              <Await
                resolve={chartData}
                errorElement={
                  <div className="text-red-500">Failed to load chart.</div>
                }
              >
                {(data) => <MacroChart chartData={data} />}
              </Await>
            </Suspense>
          </section>
          <PortfolioSection />
        </div>
      </main>
    </div>
  );
}
