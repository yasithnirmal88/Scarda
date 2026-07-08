import { useState } from 'react';
import type { MaintenanceLog } from '../../types';
import { Pagination } from '../common/Pagination';
import { SearchBar } from '../common/SearchBar';
import { StatusChip } from '../common/StatusChip';

interface MaintenanceTableProps {
  data: MaintenanceLog[];
}

export function MaintenanceTable({ data }: MaintenanceTableProps) {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const filtered = data.filter(
    (m) =>
      m.description.toLowerCase().includes(search.toLowerCase()) ||
      m.section.toLowerCase().includes(search.toLowerCase()),
  );
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  const statusVariant = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'scheduled': return 'info';
      default: return 'default';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <SearchBar value={search} onChange={setSearch} placeholder="Search maintenance logs..." />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700 text-left text-xs text-gray-500 dark:text-gray-400 uppercase">
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Section</th>
              <th className="px-4 py-3 font-medium">Description</th>
              <th className="px-4 py-3 font-medium">Technician</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((m) => (
              <tr key={m.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                <td className="px-4 py-3 text-gray-500">{m.date}</td>
                <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{m.section}</td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{m.description}</td>
                <td className="px-4 py-3 text-gray-500">{m.technician}</td>
                <td className="px-4 py-3">
                  <StatusChip label={m.status.replace('_', ' ')} variant={statusVariant(m.status)} />
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
