"use client";

import { ReactNode } from "react";

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`skeleton ${className}`} aria-hidden="true" />;
}

export function SkeletonText({ lines = 3, className = "" }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-2 ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`skeleton h-3.5 rounded ${
            i === lines - 1 && lines > 1 ? "w-3/5" : i === 0 ? "w-full" : "w-4/5"
          }`}
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ children, className = "" }: { children?: ReactNode; className?: string }) {
  return (
    <div className={`card p-6 ${className}`} aria-hidden="true">
      {children || (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-28 rounded" />
            <Skeleton className="h-5 w-16 rounded-full" />
          </div>
          <Skeleton className="h-6 w-3/4 rounded" />
          <SkeletonText lines={2} />
        </div>
      )}
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading dashboard…">
      {/* Title */}
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-32 rounded" />
          <Skeleton className="h-8 w-64 rounded-lg" />
          <Skeleton className="h-4 w-48 rounded" />
        </div>
        <Skeleton className="h-10 w-28 rounded-lg" />
      </div>

      {/* 4 Stat Cards */}
      <div className="dashboard-stats">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="card stat-card p-5">
            <Skeleton className="h-11 w-11 rounded-xl" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-3 w-24 rounded" />
              <Skeleton className="h-7 w-16 rounded" />
              <Skeleton className="h-3 w-28 rounded" />
            </div>
          </div>
        ))}
      </div>

      {/* Hero Next Step & Evidence Spotlight */}
      <div className="dashboard-grid">
        <div className="card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-4 rounded-full" />
            <Skeleton className="h-3.5 w-36 rounded" />
          </div>
          <Skeleton className="h-6 w-3/4 rounded-lg" />
          <SkeletonText lines={2} />
          <div className="flex items-center justify-between pt-2">
            <div className="flex gap-4">
              <Skeleton className="h-4 w-20 rounded" />
              <Skeleton className="h-4 w-20 rounded" />
            </div>
            <Skeleton className="h-10 w-36 rounded-lg" />
          </div>
          <Skeleton className="h-2 w-full rounded-full" />
        </div>

        <div className="card p-6 space-y-4">
          <div className="flex justify-between items-start">
            <div className="space-y-1.5">
              <Skeleton className="h-3 w-24 rounded" />
              <Skeleton className="h-5 w-40 rounded" />
            </div>
            <Skeleton className="h-7 w-20 rounded-md" />
          </div>
          <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-100 dark:bg-zinc-800/40 dark:border-zinc-800 space-y-2">
            <Skeleton className="h-4 w-full rounded" />
            <Skeleton className="h-4 w-4/5 rounded" />
          </div>
          <div className="flex items-center gap-3 pt-2">
            <Skeleton className="h-8 w-8 rounded-lg" />
            <div className="space-y-1 flex-1">
              <Skeleton className="h-3.5 w-28 rounded" />
              <Skeleton className="h-3 w-36 rounded" />
            </div>
          </div>
        </div>
      </div>

      {/* Applications Preview */}
      <div className="card p-6 space-y-4">
        <div className="flex justify-between items-center">
          <div className="space-y-1">
            <Skeleton className="h-3 w-20 rounded" />
            <Skeleton className="h-5 w-36 rounded" />
          </div>
          <Skeleton className="h-8 w-20 rounded-md" />
        </div>
        <div className="space-y-3 pt-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between p-3.5 rounded-lg border border-zinc-100 dark:border-zinc-800/60">
              <div className="flex items-center gap-3">
                <Skeleton className="h-9 w-9 rounded-lg" />
                <div className="space-y-1.5">
                  <Skeleton className="h-4 w-36 rounded" />
                  <Skeleton className="h-3 w-48 rounded" />
                </div>
              </div>
              <Skeleton className="h-4 w-12 rounded" />
              <Skeleton className="h-6 w-20 rounded-full" />
              <Skeleton className="h-4 w-28 rounded" />
              <Skeleton className="h-4 w-4 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ProfileSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading profile…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-32 rounded" />
          <Skeleton className="h-8 w-56 rounded-lg" />
          <Skeleton className="h-4 w-64 rounded" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-10 w-28 rounded-lg" />
          <Skeleton className="h-10 w-24 rounded-lg" />
        </div>
      </div>

      {/* Readiness Banner */}
      <div className="card p-6 flex flex-col md:flex-row items-center gap-6">
        <Skeleton className="h-20 w-20 rounded-full shrink-0" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-6 w-64 rounded-lg" />
          <SkeletonText lines={2} />
        </div>
        <Skeleton className="h-9 w-28 rounded-lg shrink-0" />
      </div>

      {/* Tabs */}
      <div className="flex gap-3 border-b border-zinc-200 dark:border-zinc-800 pb-2">
        <Skeleton className="h-8 w-24 rounded-lg" />
        <Skeleton className="h-8 w-28 rounded-lg" />
        <Skeleton className="h-8 w-32 rounded-lg" />
      </div>

      {/* Profile Form Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-6 space-y-5">
          <Skeleton className="h-5 w-36 rounded" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-3.5 w-20 rounded" />
                <Skeleton className="h-10 w-full rounded-lg" />
              </div>
            ))}
          </div>
          <div className="space-y-2">
            <Skeleton className="h-3.5 w-32 rounded" />
            <Skeleton className="h-24 w-full rounded-lg" />
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <Skeleton className="h-5 w-32 rounded" />
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center gap-2.5">
                <Skeleton className="h-4 w-4 rounded-full" />
                <Skeleton className="h-4 w-full rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function ProjectsSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading projects…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-32 rounded" />
          <Skeleton className="h-8 w-56 rounded-lg" />
          <Skeleton className="h-4 w-72 rounded" />
        </div>
        <Skeleton className="h-10 w-32 rounded-lg" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="card p-5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Skeleton className="h-8 w-8 rounded-lg" />
              <div className="space-y-1.5">
                <Skeleton className="h-4 w-36 rounded" />
                <Skeleton className="h-3 w-28 rounded" />
              </div>
            </div>
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="card p-6 space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <Skeleton className="h-9 w-9 rounded-lg" />
                <Skeleton className="h-6 w-6 rounded" />
              </div>
              <Skeleton className="h-5 w-40 rounded" />
              <SkeletonText lines={2} />
              <div className="flex gap-2 flex-wrap">
                <Skeleton className="h-5 w-16 rounded-md" />
                <Skeleton className="h-5 w-14 rounded-md" />
                <Skeleton className="h-5 w-20 rounded-md" />
              </div>
            </div>
            <div className="flex items-center justify-between pt-4 border-t border-zinc-100 dark:border-zinc-800">
              <Skeleton className="h-4 w-24 rounded" />
              <Skeleton className="h-8 w-28 rounded-lg" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AddJobSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading job input…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-8 w-44 rounded-lg" />
          <Skeleton className="h-4 w-72 rounded" />
        </div>
        <Skeleton className="h-9 w-36 rounded-lg" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-6 space-y-5">
          <div className="flex gap-2">
            <Skeleton className="h-9 w-28 rounded-lg" />
            <Skeleton className="h-9 w-28 rounded-lg" />
            <Skeleton className="h-9 w-28 rounded-lg" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-32 rounded" />
            <Skeleton className="h-64 w-full rounded-xl" />
          </div>
          <div className="flex justify-between items-center pt-2">
            <Skeleton className="h-4 w-36 rounded" />
            <Skeleton className="h-11 w-40 rounded-lg" />
          </div>
        </div>

        <div className="card p-6 space-y-5">
          <Skeleton className="h-10 w-10 rounded-xl" />
          <Skeleton className="h-5 w-44 rounded" />
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex gap-3">
                <Skeleton className="h-6 w-6 rounded-full shrink-0" />
                <div className="space-y-1 flex-1">
                  <Skeleton className="h-4 w-28 rounded" />
                  <Skeleton className="h-3 w-full rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function JobAnalysisSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading job analysis…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-8 w-64 rounded-lg" />
          <Skeleton className="h-4 w-48 rounded" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-10 w-24 rounded-lg" />
          <Skeleton className="h-10 w-32 rounded-lg" />
        </div>
      </div>

      <div className="card p-6 space-y-4">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-3">
            <Skeleton className="h-12 w-12 rounded-xl" />
            <div className="space-y-1.5">
              <Skeleton className="h-5 w-40 rounded" />
              <Skeleton className="h-3.5 w-56 rounded" />
            </div>
          </div>
          <Skeleton className="h-7 w-24 rounded-full" />
        </div>
        <SkeletonText lines={3} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <Skeleton className="h-5 w-44 rounded" />
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
          <div className="flex flex-wrap gap-2 pt-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-8 w-28 rounded-lg" />
            ))}
          </div>
        </div>

        <div className="card p-6 space-y-4 flex flex-col justify-between">
          <div className="flex items-center gap-5">
            <Skeleton className="h-20 w-20 rounded-full shrink-0" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-3.5 w-32 rounded" />
              <Skeleton className="h-5 w-48 rounded" />
              <Skeleton className="h-3.5 w-full rounded" />
            </div>
          </div>
          <Skeleton className="h-3 w-full rounded-full" />
        </div>
      </div>
    </div>
  );
}

export function MatchingSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading matching…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-8 w-60 rounded-lg" />
          <Skeleton className="h-4 w-72 rounded" />
        </div>
        <Skeleton className="h-10 w-36 rounded-lg" />
      </div>

      <div className="card p-6 flex flex-col md:flex-row items-center gap-6">
        <Skeleton className="h-20 w-20 rounded-full shrink-0" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-3.5 w-48 rounded" />
          <Skeleton className="h-6 w-64 rounded-lg" />
          <Skeleton className="h-4 w-5/6 rounded" />
        </div>
        <div className="flex gap-4 shrink-0">
          <Skeleton className="h-12 w-16 rounded-lg" />
          <Skeleton className="h-12 w-16 rounded-lg" />
          <Skeleton className="h-12 w-16 rounded-lg" />
        </div>
      </div>

      <div className="flex gap-2">
        <Skeleton className="h-9 w-20 rounded-lg" />
        <Skeleton className="h-9 w-20 rounded-lg" />
        <Skeleton className="h-9 w-20 rounded-lg" />
      </div>

      <div className="card p-6 space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center justify-between p-3.5 rounded-lg border border-zinc-100 dark:border-zinc-800">
            <div className="flex items-center gap-3 flex-1">
              <Skeleton className="h-5 w-5 rounded-full" />
              <div className="space-y-1">
                <Skeleton className="h-4 w-32 rounded" />
                <Skeleton className="h-3 w-20 rounded" />
              </div>
            </div>
            <Skeleton className="h-6 w-20 rounded-full" />
            <div className="space-y-1 flex-1 px-4">
              <Skeleton className="h-4 w-48 rounded" />
              <Skeleton className="h-3 w-36 rounded" />
            </div>
            <Skeleton className="h-4 w-4 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function ClarificationsSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading questions…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-32 rounded" />
          <Skeleton className="h-8 w-72 rounded-lg" />
          <Skeleton className="h-4 w-60 rounded" />
        </div>
        <Skeleton className="h-9 w-32 rounded-lg" />
      </div>

      <div className="card p-4 space-y-2">
        <div className="flex justify-between">
          <Skeleton className="h-4 w-36 rounded" />
          <Skeleton className="h-4 w-24 rounded" />
        </div>
        <Skeleton className="h-2.5 w-full rounded-full" />
      </div>

      <div className="space-y-4">
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="card p-6 flex gap-4">
            <Skeleton className="h-8 w-8 rounded-lg shrink-0" />
            <div className="space-y-3 flex-1">
              <div className="flex justify-between">
                <Skeleton className="h-5 w-24 rounded-full" />
                <Skeleton className="h-5 w-5 rounded-full" />
              </div>
              <Skeleton className="h-6 w-3/4 rounded" />
              <SkeletonText lines={2} />
              <Skeleton className="h-20 w-full rounded-lg" />
              <Skeleton className="h-9 w-28 rounded-lg" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function CvGenerationSkeleton() {
  return (
    <div className="page-frame flex items-center justify-center min-h-[60vh] animate-fadeIn" aria-label="Generating CV…">
      <div className="card max-w-lg w-full p-8 text-center space-y-6">
        <div className="flex justify-center">
          <Skeleton className="h-24 w-24 rounded-full" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-40 mx-auto rounded" />
          <Skeleton className="h-7 w-64 mx-auto rounded-lg" />
          <Skeleton className="h-4 w-80 mx-auto rounded" />
        </div>
        <div className="space-y-3 pt-4 text-left">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg border border-zinc-100 dark:border-zinc-800">
              <Skeleton className="h-5 w-5 rounded-full" />
              <Skeleton className="h-4 w-44 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function CvEditorSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading CV editor…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-8 w-44 rounded-lg" />
          <Skeleton className="h-4 w-60 rounded" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-10 w-24 rounded-lg" />
          <Skeleton className="h-10 w-28 rounded-lg" />
        </div>
      </div>

      <div className="flex justify-between items-center pb-2">
        <div className="flex gap-2">
          <Skeleton className="h-8 w-20 rounded-lg" />
          <Skeleton className="h-8 w-20 rounded-lg" />
          <Skeleton className="h-8 w-20 rounded-lg" />
        </div>
        <Skeleton className="h-5 w-28 rounded" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          <div className="card p-5 space-y-4">
            <div className="flex justify-between items-center">
              <Skeleton className="h-5 w-28 rounded" />
              <Skeleton className="h-7 w-16 rounded-md" />
            </div>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="p-3.5 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-3">
                <div className="flex justify-between items-center">
                  <Skeleton className="h-4 w-32 rounded" />
                  <Skeleton className="h-4 w-4 rounded" />
                </div>
                <Skeleton className="h-16 w-full rounded-lg" />
              </div>
            ))}
            <Skeleton className="h-10 w-full rounded-lg" />
          </div>
        </div>

        <div className="card p-8 min-h-[500px] shadow-md border border-zinc-200/80 dark:border-zinc-800 space-y-6">
          <div className="flex justify-between border-b border-zinc-200 dark:border-zinc-800 pb-4">
            <div className="space-y-2">
              <Skeleton className="h-7 w-44 rounded" />
              <Skeleton className="h-4 w-36 rounded" />
            </div>
            <div className="space-y-1">
              <Skeleton className="h-3 w-36 rounded" />
              <Skeleton className="h-3 w-28 rounded" />
            </div>
          </div>
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-5 w-28 rounded" />
              <SkeletonText lines={3} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function AtsAnalysisSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading ATS analysis…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-8 w-44 rounded-lg" />
          <Skeleton className="h-4 w-72 rounded" />
        </div>
        <Skeleton className="h-10 w-36 rounded-lg" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-6 flex items-center gap-6">
          <Skeleton className="h-24 w-24 rounded-full shrink-0" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-3.5 w-28 rounded" />
            <Skeleton className="h-6 w-40 rounded" />
            <SkeletonText lines={2} />
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <Skeleton className="h-5 w-36 rounded" />
            <Skeleton className="h-6 w-16 rounded-full" />
          </div>
          <Skeleton className="h-3 w-full rounded-full" />
          <div className="flex gap-2 flex-wrap">
            <Skeleton className="h-6 w-20 rounded-md" />
            <Skeleton className="h-6 w-24 rounded-md" />
            <Skeleton className="h-6 w-18 rounded-md" />
          </div>
        </div>
      </div>

      <div className="card p-6 space-y-3">
        <Skeleton className="h-5 w-44 rounded mb-4" />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center justify-between p-3.5 rounded-lg border border-zinc-100 dark:border-zinc-800">
            <div className="flex items-center gap-3">
              <Skeleton className="h-5 w-5 rounded-full" />
              <div className="space-y-1">
                <Skeleton className="h-4 w-40 rounded" />
                <Skeleton className="h-3 w-56 rounded" />
              </div>
            </div>
            <Skeleton className="h-6 w-16 rounded-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function CoverEmailSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading cover email…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-8 w-44 rounded-lg" />
          <Skeleton className="h-4 w-72 rounded" />
        </div>
        <Skeleton className="h-10 w-36 rounded-lg" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-6 space-y-5">
          <Skeleton className="h-5 w-32 rounded" />
          <div className="space-y-2">
            <Skeleton className="h-3.5 w-16 rounded" />
            <Skeleton className="h-10 w-full rounded-lg" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-3.5 w-16 rounded" />
            <Skeleton className="h-64 w-full rounded-xl" />
          </div>
          <div className="flex gap-3">
            <Skeleton className="h-10 w-28 rounded-lg" />
            <Skeleton className="h-10 w-28 rounded-lg" />
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <Skeleton className="h-10 w-10 rounded-xl" />
          <Skeleton className="h-5 w-40 rounded" />
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-2.5">
                <Skeleton className="h-4 w-4 rounded-full" />
                <Skeleton className="h-4 w-full rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function InterviewSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading interview prep…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-8 w-56 rounded-lg" />
          <Skeleton className="h-4 w-72 rounded" />
        </div>
        <Skeleton className="h-10 w-36 rounded-lg" />
      </div>

      <div className="card p-6 flex flex-col md:flex-row items-center gap-6">
        <Skeleton className="h-14 w-14 rounded-xl shrink-0" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-3.5 w-32 rounded" />
          <Skeleton className="h-6 w-56 rounded-lg" />
          <Skeleton className="h-4 w-72 rounded" />
        </div>
        <div className="w-40 space-y-1.5 shrink-0">
          <Skeleton className="h-4 w-20 rounded" />
          <Skeleton className="h-2.5 w-full rounded-full" />
        </div>
      </div>

      <div className="flex gap-2">
        <Skeleton className="h-8 w-16 rounded-lg" />
        <Skeleton className="h-8 w-20 rounded-lg" />
        <Skeleton className="h-8 w-20 rounded-lg" />
      </div>

      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="card p-6 flex gap-4">
            <Skeleton className="h-8 w-8 rounded-lg shrink-0" />
            <div className="space-y-3 flex-1">
              <div className="flex justify-between">
                <Skeleton className="h-5 w-24 rounded-full" />
                <Skeleton className="h-5 w-20 rounded-full" />
              </div>
              <Skeleton className="h-5 w-4/5 rounded" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-lg border border-zinc-100 dark:border-zinc-800 space-y-1.5">
                  <Skeleton className="h-3 w-24 rounded" />
                  <Skeleton className="h-3.5 w-full rounded" />
                </div>
                <div className="p-3 rounded-lg border border-zinc-100 dark:border-zinc-800 space-y-1.5">
                  <Skeleton className="h-3 w-24 rounded" />
                  <Skeleton className="h-3.5 w-full rounded" />
                </div>
              </div>
              <Skeleton className="h-8 w-36 rounded-lg" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ApplicationsSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading applications…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-32 rounded" />
          <Skeleton className="h-8 w-44 rounded-lg" />
          <Skeleton className="h-4 w-64 rounded" />
        </div>
        <Skeleton className="h-10 w-28 rounded-lg" />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="card p-4 space-y-1.5">
            <Skeleton className="h-3 w-20 rounded" />
            <Skeleton className="h-7 w-12 rounded" />
          </div>
        ))}
      </div>

      <div className="card p-6 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between gap-3">
          <Skeleton className="h-10 w-72 rounded-lg" />
          <Skeleton className="h-10 w-36 rounded-lg" />
        </div>

        <div className="space-y-3 pt-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between p-3.5 rounded-lg border border-zinc-100 dark:border-zinc-800">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="space-y-1.5">
                  <Skeleton className="h-4 w-36 rounded" />
                  <Skeleton className="h-3 w-44 rounded" />
                </div>
              </div>
              <Skeleton className="h-4 w-12 rounded" />
              <Skeleton className="h-7 w-24 rounded-lg" />
              <Skeleton className="h-4 w-32 rounded" />
              <Skeleton className="h-4 w-20 rounded" />
              <Skeleton className="h-6 w-6 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ApplicationDetailSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading application detail…">
      <Skeleton className="h-4 w-36 rounded mb-4" />
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-28 rounded" />
          <Skeleton className="h-8 w-64 rounded-lg" />
          <Skeleton className="h-4 w-48 rounded" />
        </div>
        <Skeleton className="h-7 w-24 rounded-full" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6 space-y-4">
            <div className="flex justify-between items-center">
              <Skeleton className="h-5 w-40 rounded" />
              <Skeleton className="h-8 w-28 rounded-lg" />
            </div>
            <div className="flex gap-2 overflow-x-auto py-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-8 w-20 rounded-lg shrink-0" />
              ))}
            </div>
          </div>

          <div className="card p-6 space-y-4">
            <Skeleton className="h-5 w-28 rounded" />
            <Skeleton className="h-28 w-full rounded-lg" />
            <div className="flex justify-between items-center">
              <Skeleton className="h-3 w-24 rounded" />
              <Skeleton className="h-8 w-24 rounded-lg" />
            </div>
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <Skeleton className="h-12 w-12 rounded-xl" />
          <Skeleton className="h-5 w-36 rounded" />
          <Skeleton className="h-4 w-44 rounded" />
          <div className="space-y-2 pt-4 border-t border-zinc-100 dark:border-zinc-800">
            <Skeleton className="h-4 w-full rounded" />
            <Skeleton className="h-4 w-full rounded" />
            <Skeleton className="h-4 w-full rounded" />
          </div>
        </div>
      </div>
    </div>
  );
}

export function SettingsSkeleton() {
  return (
    <div className="page-frame animate-fadeIn" aria-label="Loading settings…">
      <div className="view-title">
        <div className="space-y-2">
          <Skeleton className="h-3.5 w-24 rounded" />
          <Skeleton className="h-8 w-36 rounded-lg" />
          <Skeleton className="h-4 w-72 rounded" />
        </div>
        <Skeleton className="h-10 w-32 rounded-lg" />
      </div>

      <div className="space-y-6">
        <div className="card p-6 space-y-5">
          <Skeleton className="h-5 w-36 rounded" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-3.5 w-24 rounded" />
                <Skeleton className="h-10 w-full rounded-lg" />
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <Skeleton className="h-5 w-32 rounded" />
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between p-2">
                <div className="space-y-1">
                  <Skeleton className="h-4 w-40 rounded" />
                  <Skeleton className="h-3 w-56 rounded" />
                </div>
                <Skeleton className="h-5 w-10 rounded-full" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function LandingSkeleton() {
  return (
    <div className="marketing-page animate-fadeIn" aria-label="Loading page…">
      <div className="marketing-header">
        <div className="marketing-inner flex justify-between items-center py-4">
          <Skeleton className="h-8 w-36 rounded-lg" />
          <div className="flex gap-4">
            <Skeleton className="h-8 w-20 rounded-md" />
            <Skeleton className="h-8 w-32 rounded-md" />
          </div>
        </div>
      </div>
      <div className="page-frame py-16 space-y-12">
        <div className="max-w-2xl mx-auto text-center space-y-4">
          <Skeleton className="h-6 w-48 mx-auto rounded-full" />
          <Skeleton className="h-12 w-4/5 mx-auto rounded-xl" />
          <Skeleton className="h-5 w-3/4 mx-auto rounded" />
        </div>
        <div className="max-w-4xl mx-auto h-72 card p-6" />
      </div>
    </div>
  );
}

export function AuthSkeleton() {
  return (
    <div className="auth-page min-h-screen flex items-center justify-center p-6 animate-fadeIn" aria-label="Loading…">
      <div className="card max-w-4xl w-full p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <Skeleton className="h-8 w-36 rounded-lg" />
          <SkeletonText lines={4} />
        </div>
        <div className="space-y-4">
          <Skeleton className="h-6 w-48 rounded" />
          <Skeleton className="h-10 w-full rounded-lg" />
          <Skeleton className="h-10 w-full rounded-lg" />
          <Skeleton className="h-11 w-full rounded-lg" />
        </div>
      </div>
    </div>
  );
}

export function OnboardingSkeleton() {
  return (
    <div className="onboarding-page min-h-screen p-6 max-w-2xl mx-auto space-y-8 animate-fadeIn" aria-label="Loading onboarding…">
      <div className="flex justify-between items-center">
        <Skeleton className="h-8 w-36 rounded-lg" />
        <Skeleton className="h-4 w-32 rounded" />
      </div>
      <div className="flex justify-between gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-10 flex-1 rounded-lg" />
        ))}
      </div>
      <div className="card p-8 space-y-6">
        <Skeleton className="h-6 w-56 rounded" />
        <Skeleton className="h-10 w-full rounded-lg" />
        <Skeleton className="h-10 w-full rounded-lg" />
        <div className="flex justify-between pt-4">
          <Skeleton className="h-10 w-24 rounded-lg" />
          <Skeleton className="h-10 w-32 rounded-lg" />
        </div>
      </div>
    </div>
  );
}
