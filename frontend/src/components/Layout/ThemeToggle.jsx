/**
 * ThemeToggle.jsx — Dark / light mode toggle button.
 *
 * Persists the preference in localStorage and toggles the `dark` class
 * on <html> so Tailwind's dark: variants take effect.
 */

import { useState, useEffect } from "react";
import { Sun, Moon } from "lucide-react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    // Default to dark unless the user previously chose light
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("theme");
      return stored ? stored === "dark" : true;
    }
    return true;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [dark]);

  return (
    <button
      onClick={() => setDark((prev) => !prev)}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      className="relative p-2.5 rounded-xl bg-white/10 dark:bg-white/5 backdrop-blur-sm
                 border border-white/10 hover:border-white/20
                 transition-all duration-300 hover:scale-105 active:scale-95
                 text-slate-700 dark:text-slate-300 cursor-pointer"
    >
      {/* Animated icon swap */}
      <Sun
        size={20}
        className={`absolute inset-0 m-auto transition-all duration-300
          ${dark ? "opacity-0 rotate-90 scale-0" : "opacity-100 rotate-0 scale-100"}`}
      />
      <Moon
        size={20}
        className={`transition-all duration-300
          ${dark ? "opacity-100 rotate-0 scale-100" : "opacity-0 -rotate-90 scale-0"}`}
      />
    </button>
  );
}
