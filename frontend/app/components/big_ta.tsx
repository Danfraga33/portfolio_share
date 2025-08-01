import React from "react";

const Big_TA = () => {
  return (
    <div className="max-w-xs rounded-md border border-border bg-card p-3">
      <h4 className="mb-2 text-sm font-medium text-foreground">
        Investment Strategy
      </h4>
      <div className="space-y-1">
        <div className="flex items-center justify-between rounded-sm bg-red-50/50 px-2 py-1 dark:bg-red-950/10">
          <span className="font-mono text-xs font-medium text-foreground">
            &gt; 2
          </span>
          <span className="text-xs font-medium text-red-600/70 dark:text-red-400/70">
            Big Sell
          </span>
        </div>

        <div className="flex items-center justify-between rounded-sm bg-blue-50/50 px-2 py-1 dark:bg-blue-950/10">
          <span className="font-mono text-xs font-medium text-foreground">
            -2 to 2
          </span>
          <span className="text-xs font-medium text-blue-600/70 dark:text-blue-400/70">
            Stan TA
          </span>
        </div>

        <div className="flex items-center justify-between rounded-sm bg-green-50/50 px-2 py-1 dark:bg-green-950/10">
          <span className="font-mono text-xs font-medium text-foreground">
            &lt; -2
          </span>
          <span className="text-xs font-medium text-green-600/70 dark:text-green-400/70">
            Big Buy
          </span>
        </div>
      </div>

      <div className="mt-3 border-t border-border/50 pt-2">
        <p className="text-xs text-muted-foreground">
          Stan TA: Momentum market – follow 30WMA signals for trend direction.
        </p>
      </div>
    </div>
  );
};

export default Big_TA;
