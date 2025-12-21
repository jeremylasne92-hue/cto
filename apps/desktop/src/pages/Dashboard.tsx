import { motion } from 'framer-motion'
import { Activity, BookOpen, Trophy, Clock } from 'lucide-react'
import { cn } from '../lib/utils'

function StatCard({ title, value, icon: Icon, trend, color }: any) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 rounded-2xl relative overflow-hidden group"
        >
            <div className={cn("absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity", color)}>
                <Icon size={80} />
            </div>
            <div className="relative z-10">
                <div className={cn("inline-flex p-2 rounded-lg mb-4 bg-white/5", color)}>
                    <Icon size={24} className="text-white" />
                </div>
                <h3 className="text-muted-foreground font-medium text-sm">{title}</h3>
                <p className="text-3xl font-bold text-white mt-1 tabular-nums">{value}</p>

                {trend && (
                    <div className="flex items-center gap-2 mt-4 text-xs">
                        <span className="text-emerald-400 font-medium">{trend}</span>
                        <span className="text-muted-foreground">vs last week</span>
                    </div>
                )}
            </div>
        </motion.div>
    )
}

export default function Dashboard() {
    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Welcome back, Traveler</h1>
                <p className="text-muted-foreground">Your cognitive journey continues. Local systems optimal.</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <StatCard
                    title="Cards Due"
                    value="42"
                    icon={BookOpen}
                    trend="+12%"
                    color="text-blue-400"
                />
                <StatCard
                    title="Daily Streak"
                    value="7 Days"
                    icon={Activity}
                    trend="On fire!"
                    color="text-orange-400"
                />
                <StatCard
                    title="Mastery Level"
                    value="Lvl 12"
                    icon={Trophy}
                    color="text-yellow-400"
                />
                <StatCard
                    title="Study Time"
                    value="4.5h"
                    icon={Clock}
                    trend="+30m"
                    color="text-purple-400"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-96">
                <div className="glass-card rounded-2xl p-6 lg:col-span-2">
                    <h3 className="font-semibold text-white mb-4">Activity Map</h3>
                    <div className="h-full flex items-center justify-center text-muted-foreground bg-white/5 rounded-xl border border-white/5 border-dashed">
                        Chart Placeholder
                    </div>
                </div>
                <div className="glass-card rounded-2xl p-6">
                    <h3 className="font-semibold text-white mb-4">Quick Actions</h3>
                    <div className="space-y-3">
                        <button className="w-full p-3 rounded-lg bg-primary/20 hover:bg-primary/30 text-primary-foreground transition-colors text-sm font-medium border border-primary/20">
                            Create New Deck
                        </button>
                        <button className="w-full p-3 rounded-lg bg-white/5 hover:bg-white/10 text-white transition-colors text-sm font-medium border border-white/10">
                            Import Files
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
