/**
 * Header.jsx — Top-level app header.
 *
 * Displays the gradient "Convert" logo, a subtitle, and the theme toggle.
 */

import ThemeToggle from "./ThemeToggle";
import { ArrowRightLeft } from "lucide-react";

export default function Header() {
  return (
    <header className="w-full py-6 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        {/* Logo / title */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-500/25">
            <ArrowRightLeft size={24} className="text-white" />
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
              Convert
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 -mt-0.5">
              Universal File Converter &amp; Compressor
            </p>
          </div>
        </div>

        {/* Theme toggle */}
        <ThemeToggle />
      </div>
    </header>
  );
}
