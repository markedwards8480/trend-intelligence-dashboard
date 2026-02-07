import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const trendingColors = [
  { color: 'Soft Pink', count: 234 },
  { color: 'Black', count: 198 },
  { color: 'White', count: 187 },
  { color: 'Beige', count: 156 },
  { color: 'Purple', count: 134 },
]

const categoryDistribution = [
  { name: 'Dresses', value: 28, fill: '#EC4899' },
  { name: 'Tops', value: 22, fill: '#F472B6' },
  { name: 'Pants', value: 18, fill: '#DB2777' },
  { name: 'Accessories', value: 16, fill: '#BE185D' },
  { name: 'Footwear', value: 16, fill: '#9D174D' },
]

const styleTagMomentum = [
  { date: 'Week 1', 'Y2K': 45, Minimalist: 32, Streetwear: 28, Vintage: 18 },
  { date: 'Week 2', 'Y2K': 62, Minimalist: 38, Streetwear: 35, Vintage: 22 },
  { date: 'Week 3', 'Y2K': 89, Minimalist: 42, Streetwear: 48, Vintage: 28 },
  { date: 'Week 4', 'Y2K': 134, Minimalist: 45, Streetwear: 67, Vintage: 32 },
]

const velocityLeaders = [
  { id: '1', trend: 'Y2K Maxi Dresses', category: 'Dresses', growth: 245, engagement: 145000 },
  { id: '2', trend: 'Mesh Crop Tops', category: 'Tops', growth: 198, engagement: 134000 },
  { id: '3', trend: 'Cargo Pants Pink', category: 'Pants', growth: 176, engagement: 167000 },
  { id: '4', trend: 'Gold Statement Jewelry', category: 'Accessories', growth: 145, engagement: 98000 },
  { id: '5', trend: 'Platform Sneakers', category: 'Footwear', growth: 132, engagement: 123000 },
]

export default function Analytics() {
  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">Analytics</h1>
        <p className="text-lg text-accent-600">Deep dive into trend data and insights</p>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Trending Colors Chart */}
        <div className="card p-6">
          <h2 className="font-display font-bold text-accent-900 mb-6">Top Trending Colors</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trendingColors}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="color" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FDF2F8',
                  border: '1px solid #F472B6',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="count" fill="#EC4899" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution */}
        <div className="card p-6">
          <h2 className="font-display font-bold text-accent-900 mb-6">Category Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name} ${value}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FDF2F8',
                  border: '1px solid #F472B6',
                  borderRadius: '8px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Style Tags Momentum */}
      <div className="card p-6 mb-8">
        <h2 className="font-display font-bold text-accent-900 mb-6">Style Tag Momentum (4-Week Trend)</h2>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={styleTagMomentum}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="date" stroke="#6B7280" />
            <YAxis stroke="#6B7280" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#FDF2F8',
                border: '1px solid #F472B6',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Line type="monotone" dataKey="Y2K" stroke="#EC4899" strokeWidth={2} />
            <Line type="monotone" dataKey="Minimalist" stroke="#F472B6" strokeWidth={2} />
            <Line type="monotone" dataKey="Streetwear" stroke="#DB2777" strokeWidth={2} />
            <Line type="monotone" dataKey="Vintage" stroke="#BE185D" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Velocity Leaders Table */}
      <div className="card overflow-hidden">
        <div className="p-6 border-b border-accent-100">
          <h2 className="font-display font-bold text-accent-900">Velocity Leaders</h2>
          <p className="text-sm text-accent-600 mt-1">Top 5 fastest-growing trends this week</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-accent-50 border-b border-accent-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-accent-900 uppercase">Trend</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-accent-900 uppercase">Category</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-accent-900 uppercase">Growth %</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-accent-900 uppercase">Engagement</th>
                <th className="px-6 py-3 text-center text-xs font-semibold text-accent-900 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-accent-100">
              {velocityLeaders.map((item, idx) => (
                <tr key={item.id} className="hover:bg-accent-50 transition-colors">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-accent-900">#{idx + 1}</p>
                      <p className="text-sm text-accent-700 font-display font-bold">{item.trend}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="badge-primary text-xs">{item.category}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <span className="text-lg">📈</span>
                      <span className="font-display font-bold text-green-600">+{item.growth}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <p className="font-medium text-accent-900">{(item.engagement / 1000).toFixed(0)}k</p>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                      Rising
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bottom Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="card p-6">
          <h3 className="font-display font-bold text-accent-900 mb-4">Key Insight</h3>
          <p className="text-accent-700 leading-relaxed">
            Y2K aesthetic is dominating with 245% growth week-over-week. Soft pink and beige colors are commanding
            the color palette.
          </p>
        </div>
        <div className="card p-6">
          <h3 className="font-display font-bold text-accent-900 mb-4">Next Hot Trend</h3>
          <p className="text-accent-700 leading-relaxed">
            Vintage cargo pants combined with minimalist accessories show emerging momentum. Watch for growth in the
            coming weeks.
          </p>
        </div>
        <div className="card p-6">
          <h3 className="font-display font-bold text-accent-900 mb-4">Target Demo</h3>
          <p className="text-accent-700 leading-relaxed">
            Ages 18-24 drive the highest engagement. TikTok and Instagram are the primary discovery platforms for your
            audience.
          </p>
        </div>
      </div>
    </div>
  )
}
