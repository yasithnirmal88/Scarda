export function Navbar() {
  return (
    <header className="h-16 bg-white border-b flex items-center justify-between px-6">
      <h1 className="text-lg font-semibold text-gray-800">Solar AIM</h1>
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-600">John Doe</span>
        <div className="w-8 h-8 rounded-full bg-gray-300" />
      </div>
    </header>
  );
}
