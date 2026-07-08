export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const dims = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-8 w-8' : 'h-6 w-6';
  return (
    <div className="flex items-center justify-center">
      <div
        className={`${dims} border-2 border-solar-200 border-t-solar-600 rounded-full animate-spin`}
      />
    </div>
  );
}
