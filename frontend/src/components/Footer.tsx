import { APP_NAME, APP_VERSION } from "@/lib/app";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-4 text-center text-xs text-slate-500">
        {APP_NAME} · Version {APP_VERSION}
      </div>
    </footer>
  );
}
