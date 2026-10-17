"use client";

import {
  ArrowLeft,
  ArrowRight,
  CheckCircle,
  Eye,
  EyeSlash,
  LockSimple,
  Sparkle,
  WarningCircle,
} from "@phosphor-icons/react";
import { useState } from "react";
import { Button, Field } from "@/components/ui";
import { useLogin, useRegister } from "@/hooks/use-auth";
import { toUserFriendlyMessage } from "@/lib/api/errors";

export function AuthPage({
  initialMode = "register",
  onBack,
  onComplete,
}: {
  initialMode?: "register" | "login";
  onBack: () => void;
  onComplete: () => void;
}) {
  const [mode, setMode] = useState<"register" | "login">(initialMode);
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loginMutation = useLogin();
  const registerMutation = useRegister();

  const isPending = loginMutation.isPending || registerMutation.isPending;

  const handleTabSwitch = (newMode: "register" | "login") => {
    setMode(newMode);
    setErrorMessage(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage(null);

    const formData = new FormData(event.currentTarget);
    const email = (formData.get("email") as string)?.trim();
    const password = formData.get("password") as string;
    const name = (formData.get("name") as string)?.trim();

    try {
      if (mode === "register") {
        if (!name) {
          setErrorMessage("Please enter your full name.");
          return;
        }
        await registerMutation.mutateAsync({
          email,
          password,
          full_name: name,
        });
      } else {
        await loginMutation.mutateAsync({
          email,
          password,
        });
      }
      onComplete();
    } catch (error) {
      setErrorMessage(toUserFriendlyMessage(error));
    }
  };

  return (
    <div className="auth-page">
      <button className="auth-back" onClick={onBack}>
        <ArrowLeft size={17} aria-hidden="true" /> Back to home
      </button>
      <div className="auth-layout">
        <section className="auth-story">
          <div className="auth-story-inner">
            <div className="brand">
              <span className="brand-mark">
                <Sparkle size={17} weight="fill" aria-hidden="true" />
              </span>
              <span className="brand-name">AI CV Maker</span>
            </div>
            <div className="auth-quote">
              <p>“The most useful version of your career story is the one you can verify.”</p>
              <span>Built around your evidence, not around a blank prompt.</span>
            </div>
            <div className="auth-list">
              <div>
                <CheckCircle size={18} weight="fill" aria-hidden="true" />
                <span>Import once, tailor many times</span>
              </div>
              <div>
                <CheckCircle size={18} weight="fill" aria-hidden="true" />
                <span>Review every AI suggestion</span>
              </div>
              <div>
                <CheckCircle size={18} weight="fill" aria-hidden="true" />
                <span>Keep your applications organized</span>
              </div>
            </div>
          </div>
        </section>

        <section className="auth-form-wrap">
          <div className="auth-form-card">
            <div className="auth-heading">
              <p className="eyebrow">
                {mode === "register" ? "Start with your source of truth" : "Welcome back"}
              </p>
              <h1>
                {mode === "register" ? "Create your workspace" : "Sign in to your workspace"}
              </h1>
              <p>
                {mode === "register"
                  ? "A few details now. A much clearer application process later."
                  : "Pick up where you left off with your profile and applications."}
              </p>
            </div>

            <div className="auth-tabs">
              <button
                type="button"
                className={mode === "register" ? "active" : ""}
                onClick={() => handleTabSwitch("register")}
              >
                Create account
              </button>
              <button
                type="button"
                className={mode === "login" ? "active" : ""}
                onClick={() => handleTabSwitch("login")}
              >
                Sign in
              </button>
            </div>

            {errorMessage && (
              <div
                role="alert"
                className="p-3 mb-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-start gap-2 animate-fadeIn"
              >
                <WarningCircle size={18} className="shrink-0 mt-0.5" aria-hidden="true" />
                <span>{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form">
              {mode === "register" ? (
                <Field
                  label="Full name"
                  name="name"
                  autoComplete="name"
                  placeholder="Aarav Mehta"
                  disabled={isPending}
                  required
                />
              ) : null}

              <Field
                label="Email address"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                disabled={isPending}
                required
              />

              <label className="field">
                <span className="field-label">Password</span>
                <div className="password-input">
                  <input
                    className="input"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete={mode === "register" ? "new-password" : "current-password"}
                    placeholder="At least 8 characters"
                    minLength={8}
                    disabled={isPending}
                    required
                  />
                  <button
                    type="button"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeSlash size={18} aria-hidden="true" />
                    ) : (
                      <Eye size={18} aria-hidden="true" />
                    )}
                  </button>
                </div>
              </label>

              {mode === "login" ? (
                <div className="form-meta">
                  <label className="checkbox-label">
                    <input type="checkbox" /> <span>Remember this device</span>
                  </label>
                  <button type="button" className="form-link">
                    Forgot password?
                  </button>
                </div>
              ) : (
                <p className="auth-legal">
                  By creating an account, you agree to keep your application materials honest and under your control.
                </p>
              )}

              <Button
                type="submit"
                size="lg"
                className="full-width"
                loading={isPending}
                disabled={isPending}
                icon={<ArrowRight size={18} aria-hidden="true" />}
              >
                {mode === "register" ? "Create Workspace" : "Sign In"}
              </Button>
            </form>

            <div className="auth-secure">
              <LockSimple size={14} aria-hidden="true" /> Connected to secure FastAPI authentication
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
