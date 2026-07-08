import { useState } from 'react';
import { Download } from 'lucide-react';
import type { Report } from '../../types';
import { Pagination } from '../common/Pagination';
import { SearchBar } from '../common/SearchBar';
import { StatusChip } from '../common/StatusChip';

interface ReportsTableProps {
  data: Report[];
}

export function ReportsTable({ data }: ReportsTableProps) {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const filtered = data.filter((r) => r.title.toLowerCase().includes(search.toLowerCase()));
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <SearchBar value={search} onChange={setSearch} placeholder="Search reports..." />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700 text-left text-xs text-gray-500 dark:text-gray-400 uppercase">
              <th className="px-4 py-3 font-medium">Title</th>
              <th className="px-4 py-3 font-medium">Type</th>
              <th className="px-4 py-3 font-medium">Generated</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium" />
            </tr>
          </thead>
          <tbody>
            {paged.map((r) => (
              <tr key={r.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{r.title}</td>
                <td className="px-4 py-3">
                  <StatusChip label={r.type} variant="info" />
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {new Date(r.generatedAt).toLocaleDateString()}
                </td>
                <td className="px-4 py-3">
                  <StatusChip label={r.status} variant={r.status === 'ready' ? 'success' : 'warning'} />
                </td>
                <td className="px-4 py-3">
                  <button className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-solar-600">
                    <Download size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination page={page} pageSize={pageSize} total={filtered.length} onPageChange={setPage} />
    </div>
  );
}
