export function Heatmap() {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-semibold mb-2">Heatmap</h3>
      <div className="grid grid-cols-6 gap-1">
        {Array.from({ length: 24 }).map((_, i) => (
          <div
            key={i}
            className="aspect-square rounded"
            style={{
              backgroundColor: `hsl(${120 - i * 5}, 70%, ${70 - i * 2}%)`,
            }}
          />
        ))}
      </div>
      <p className="text-xs text-gray-400 mt-2">Placeholder heatmap</p>
    </div>
  );
}
