export function Footer() {
  return (
    <footer className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-3">
      <div className="flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
        <span>&copy; {new Date().getFullYear()} Solar AIM. All rights reserved.</span>
        <span>v0.1.0</span>
      </div>
    </footer>
  );
}
