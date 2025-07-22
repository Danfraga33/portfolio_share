// app/components/ChartLoader.tsx
import React from "react";

export function ChartLoader() {
  return (
    <div className="flex h-64 w-full flex-col items-center justify-center space-y-4">
      {/* Spinning ring */}
      <div className="relative">
        <div
          className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"
          aria-label="Loading"
        />
      </div>
    </div>
  );
}
