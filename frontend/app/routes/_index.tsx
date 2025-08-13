import type { LoaderFunctionArgs, MetaFunction } from "@remix-run/node";
import { Await, defer, json, useLoaderData } from "@remix-run/react";
import { Suspense } from "react";
import { ChartLoader } from "~/components/chartLoader";
import { MacroChart } from "~/components/macro-chart";
import { PortfolioSection } from "~/components/portfolio-section";
import Strategy from "~/components/strategy";

export const loader = async ({ request }: LoaderFunctionArgs) => {
  const base = process.env.PUBLIC_API_URL;
  if (!base) {
    throw json({ message: "Missing PUBLIC_API_URL env var" }, { status: 500 });
  }

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

// Component to display the latest value
function LatestValue({
  chartData,
}: {
  chartData: Array<{ date: string; value: number }>;
}) {
  // Sort by date to ensure we get the latest value
  const sortedData = [...chartData].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
  );

  const latestEntry = sortedData[sortedData.length - 1];

  if (!latestEntry) {
    return <div className="text-muted-foreground">No data available</div>;
  }

  return (
    <div className="flex items-center gap-4">
      <span className="text-sm text-muted-foreground">Latest Value:</span>
      <span className="text-lg font-medium text-foreground">
        {latestEntry.value.toFixed(2)}
      </span>
      <span className="text-xs text-muted-foreground">
        ({new Date(latestEntry.date).toLocaleDateString()})
      </span>
    </div>
  );
}

export default function Index() {
  const { chartData } = useLoaderData<typeof loader>();

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-12">
          <section className="space-y-4">
            <section className="flex items-center justify-between">
              <h2 className="text-2xl font-light text-foreground">
                Macro Compass — Strategy for High-Conviction Moves
              </h2>
              <div>
                <Suspense
                  fallback={
                    <div className="text-muted-foreground">
                      Loading latest value...
                    </div>
                  }
                >
                  <Await
                    resolve={chartData}
                    errorElement={
                      <div className="text-red-500">
                        Failed to load latest value.
                      </div>
                    }
                  >
                    {(data) => <LatestValue chartData={data} />}
                  </Await>
                </Suspense>
              </div>
            </section>
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
            <Strategy />
          </section>
          <PortfolioSection />
        </div>
      </main>
    </div>
  );
}
