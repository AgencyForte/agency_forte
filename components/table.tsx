export function OpsTable<T extends object>({
  rows,
  columns
}: Readonly<{
  rows: T[];
  columns: Array<{ key: keyof T; label: string; render?: (row: T) => React.ReactNode }>;
}>) {
  if (rows.length === 0) {
    return null;
  }

  return (
    <div className="overflow-hidden rounded-md border border-black/10 bg-white">
      <table className="min-w-full divide-y divide-black/10 text-left text-sm">
        <thead className="bg-field text-xs uppercase text-black/60">
          <tr>
            {columns.map((column) => (
              <th className="px-4 py-3 font-semibold" key={String(column.key)}>
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-black/10">
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td className="max-w-[260px] truncate px-4 py-3 text-ink" key={String(column.key)}>
                  {column.render ? column.render(row) : String(row[column.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
