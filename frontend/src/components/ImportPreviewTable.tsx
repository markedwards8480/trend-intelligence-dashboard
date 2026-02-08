interface ParsedRow {
  name: string
  url: string
  index: number
}

export default function ImportPreviewTable({ rows }: { rows: ParsedRow[] }) {
  return (
    <div>
      <p className="text-sm font-medium text-accent-900 mb-2">
        Preview ({rows.length} site{rows.length !== 1 ? 's' : ''} found)
      </p>
      <div className="overflow-x-auto border border-accent-200 rounded-lg">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-accent-50 border-b border-accent-200">
              <th className="text-left px-3 py-2 font-medium text-accent-700 w-8">#</th>
              <th className="text-left px-3 py-2 font-medium text-accent-700">Site Name</th>
              <th className="text-left px-3 py-2 font-medium text-accent-700">URL</th>
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 10).map((row) => (
              <tr key={row.index} className="border-b border-accent-100 hover:bg-accent-50">
                <td className="px-3 py-2 text-accent-500">{row.index}</td>
                <td className="px-3 py-2 text-accent-900 font-medium">{row.name}</td>
                <td className="px-3 py-2 text-accent-600 text-xs truncate max-w-[250px]">{row.url}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length > 10 && (
          <p className="text-xs text-accent-500 px-3 py-2 bg-accent-50 border-t border-accent-200">
            ... and {rows.length - 10} more
          </p>
        )}
      </div>
    </div>
  )
}
