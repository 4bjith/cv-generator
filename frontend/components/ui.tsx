"use client";

import { Check, CheckCircle, CircleNotch, Info, WarningCircle, X } from "@phosphor-icons/react";
import { ButtonHTMLAttributes, forwardRef, InputHTMLAttributes, ReactNode, TextareaHTMLAttributes, useEffect, useRef } from "react";
import { ToastMessage } from "@/types";

type ButtonVariant = "primary" | "secondary" | "ghost" | "quiet" | "danger";

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  children,
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: ReactNode;
}) {
  return (
    <button
      className={`button button-${variant} button-${size} ${loading ? "button-loading" : ""} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading ? <CircleNotch className="spin" size={16} aria-hidden="true" /> : icon}
      <span>{children}</span>
    </button>
  );
}

export const IconButton = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement> & { label: string }>(function IconButton({ label, className = "", children, ...props }, ref) {
  return <button ref={ref} className={`icon-button ${className}`} aria-label={label} title={label} {...props}>{children}</button>;
});

export function Badge({
  tone = "neutral",
  children,
  className = "",
  style,
}: {
  tone?: string;
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
}) {
  return <span className={`badge badge-${tone} ${className}`} style={style}>{children}</span>;
}

export function Card({
  children,
  className = "",
  as: Element = "section",
  style,
  ...props
}: {
  children: ReactNode;
  className?: string;
  as?: "section" | "div" | "article";
  style?: React.CSSProperties;
} & React.HTMLAttributes<HTMLElement>) {
  return <Element className={`card ${className}`} style={style} {...props}>{children}</Element>;
}

export function SectionHeading({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="section-heading">
      <div>
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <h2>{title}</h2>
        {description ? <p className="section-description">{description}</p> : null}
      </div>
      {action ? <div className="section-heading-action">{action}</div> : null}
    </div>
  );
}

export function ProgressBar({ value, tone = "accent", label }: { value: number; tone?: string; label?: string }) {
  return (
    <div className="progress-wrap">
      {label ? <div className="progress-label"><span>{label}</span><strong>{value}%</strong></div> : null}
      <div className="progress-track" aria-label={label} role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
        <span className={`progress-fill progress-${tone}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export function Avatar({ initials, size = "md", tone = "blue" }: { initials: string; size?: "sm" | "md" | "lg"; tone?: string }) {
  return <span className={`avatar avatar-${size} avatar-${tone}`}>{initials}</span>;
}

export function Field({
  label,
  hint,
  error,
  id,
  className = "",
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label: string; hint?: string; error?: string }) {
  const generatedId = id || (props.name ? `field-${props.name}` : undefined);
  return (
    <label className={`field ${className}`} htmlFor={generatedId}>
      <span className="field-label">{label}</span>
      <input
        id={generatedId}
        className={`input ${error ? "input-error" : ""}`}
        aria-invalid={Boolean(error)}
        {...props}
      />
      {error ? <span className="field-error" role="alert">{error}</span> : hint ? <span className="field-hint">{hint}</span> : null}
    </label>
  );
}

export function TextareaField({
  label,
  hint,
  error,
  id,
  className = "",
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string; hint?: string; error?: string }) {
  const generatedId = id || (props.name ? `field-${props.name}` : undefined);
  return (
    <label className={`field ${className}`} htmlFor={generatedId}>
      <span className="field-label">{label}</span>
      <textarea
        id={generatedId}
        className={`input textarea ${error ? "input-error" : ""}`}
        aria-invalid={Boolean(error)}
        {...props}
      />
      {error ? <span className="field-error" role="alert">{error}</span> : hint ? <span className="field-hint">{hint}</span> : null}
    </label>
  );
}

export function SelectField({
  label,
  children,
  id,
  className = "",
  hint,
  error,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & { label: string; hint?: string; error?: string }) {
  const generatedId = id || (props.name ? `field-${props.name}` : undefined);
  return (
    <label className={`field ${className}`} htmlFor={generatedId}>
      <span className="field-label">{label}</span>
      <select id={generatedId} className={`input select ${error ? "input-error" : ""}`} aria-invalid={Boolean(error)} {...props}>
        {children}
      </select>
      {error ? <span className="field-error" role="alert">{error}</span> : hint ? <span className="field-hint">{hint}</span> : null}
    </label>
  );
}

export function StatusIcon({ status }: { status: "pass" | "warning" | "review" | "success" | "info" | "error" }) {
  if (status === "pass" || status === "success") return <CheckCircle className="status-icon status-success" size={18} weight="fill" aria-hidden="true" />;
  if (status === "warning" || status === "review") return <WarningCircle className="status-icon status-warning" size={18} weight="fill" aria-hidden="true" />;
  if (status === "error") return <WarningCircle className="status-icon status-error" size={18} weight="fill" aria-hidden="true" />;
  return <Info className="status-icon status-info" size={18} weight="fill" aria-hidden="true" />;
}

export function ToastViewport({ toasts, onDismiss }: { toasts: ToastMessage[]; onDismiss: (id: number) => void }) {
  return (
    <div className="toast-viewport" aria-live="polite" aria-atomic="true">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast toast-${toast.type}`} role="status">
          <StatusIcon status={toast.type} />
          <div className="toast-copy"><strong>{toast.title}</strong><span>{toast.message}</span></div>
          <button className="toast-dismiss" aria-label="Dismiss notification" onClick={() => onDismiss(toast.id)}><X size={16} aria-hidden="true" /></button>
        </div>
      ))}
    </div>
  );
}

export function Modal({
  open,
  title,
  description,
  onClose,
  children,
  footer,
}: {
  open: boolean;
  title: string;
  description?: string;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
}) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  // Manage focus only when modal opens (transitions from closed to open)
  useEffect(() => {
    if (!open) return;
    const autoFocusEl = modalRef.current?.querySelector<HTMLElement>(
      "[autofocus], [data-autofocus]"
    );
    if (autoFocusEl) {
      autoFocusEl.focus();
    } else {
      closeRef.current?.focus();
    }
  }, [open]);

  // Handle Escape key to close modal
  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onCloseRef.current();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onCloseRef.current();
      }}
    >
      <div
        ref={modalRef}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="modal-head">
          <div>
            <h2 id="modal-title">{title}</h2>
            {description ? <p>{description}</p> : null}
          </div>
          <IconButton
            label="Close dialog"
            ref={closeRef}
            onClick={() => onCloseRef.current()}
          >
            <X size={18} aria-hidden="true" />
          </IconButton>
        </div>
        <div className="modal-body">{children}</div>
        {footer ? <div className="modal-foot">{footer}</div> : null}
      </div>
    </div>
  );
}

export function InlineNotice({ tone = "info", title, children }: { tone?: "info" | "success" | "warning"; title: string; children: ReactNode }) {
  return <div className={`inline-notice notice-${tone}`}><StatusIcon status={tone} /><div><strong>{title}</strong><span>{children}</span></div></div>;
}

export function CheckMark({ checked }: { checked: boolean }) {
  return <span className={`check-mark ${checked ? "check-mark-checked" : ""}`}>{checked ? <Check size={13} weight="bold" aria-hidden="true" /> : null}</span>;
}
