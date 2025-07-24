import React from "react";

const Strategy = () => {
  return (
    <div className="max-w-xs rounded-md border border-border bg-card p-3">
      <h4 className="mb-2 text-sm font-medium text-foreground">
        Investing Rules
      </h4>
      <div className="space-y-1">
        <div className="flex items-center justify-between rounded-sm bg-red-50/50 px-2 py-1 dark:bg-red-950/10">
          <span className="font-mono text-xs font-medium text-foreground">
            &gt; 3
          </span>
          <span className="text-xs font-medium text-red-600/70 dark:text-red-400/70">
            Sell
          </span>
        </div>

        <div className="bg-red-25/30 flex items-center justify-between rounded-sm px-2 py-1 dark:bg-red-950/5">
          <span className="font-mono text-xs font-medium text-foreground">
            2
          </span>
          <span className="text-xs font-medium text-red-500/60 dark:text-red-400/60">
            Rebalance
          </span>
        </div>

        <div className="bg-green-25/30 flex items-center justify-between rounded-sm px-2 py-1 dark:bg-green-950/5">
          <span className="font-mono text-xs font-medium text-foreground">
            -1
          </span>
          <span className="text-xs font-medium text-green-500/60 dark:text-green-400/60">
            DCA
          </span>
        </div>

        <div className="flex items-center justify-between rounded-sm bg-green-50/50 px-2 py-1 dark:bg-green-950/10">
          <span className="font-mono text-xs font-medium text-foreground">
            &lt; -2
          </span>
          <span className="text-xs font-medium text-green-600/70 dark:text-green-400/70">
            Buy
          </span>
        </div>
      </div>
    </div>
  );
};

export default Strategy;
