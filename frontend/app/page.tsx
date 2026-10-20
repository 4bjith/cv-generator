"use client";

import { lazy, Suspense, useEffect, useState, useTransition } from "react";
import { AgentCommandCenter } from "@/components/agent/agent-command-center";
import { ToastViewport } from "@/components/ui";
import { ToastMessage } from "@/types";

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    setMounted(true);
  }, []);

  const addToast = (title: string, message: string, type: ToastMessage["type"] = "success") => {
    const id = Date.now() + Math.floor(Math.random() * 100000);
    setToasts((items) => [...items, { id, title, message, type }]);
    window.setTimeout(() => setToasts((items) => items.filter((item) => item.id !== id)), 4200);
  };

  const toastElement = (
    <ToastViewport
      toasts={toasts}
      onDismiss={(id) => setToasts((items) => items.filter((item) => item.id !== id))}
    />
  );

  if (!mounted) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#fafafa] font-mono text-[11px] text-[#71717a]">
        INITIALIZING COMMAND CENTER...
      </div>
    );
  }

  return (
    <>
      <AgentCommandCenter onToast={addToast} />
      {toastElement}
    </>
  );
}
