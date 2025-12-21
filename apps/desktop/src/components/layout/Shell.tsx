import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    LayoutDashboard,
    Layers,
    BrainCircuit,
    UploadCloud,
    UserCircle,
    Settings,
    Menu
} from 'lucide-react'
import { cn } from '../../lib/utils'

interface NavItem {
    icon: any
    label: string
    id: string
}

const navItems: NavItem[] = [
    { icon: LayoutDashboard, label: 'Dashboard', id: 'dashboard' },
    { icon: Layers, label: 'Decks', id: 'decks' },
    { icon: BrainCircuit, label: 'Knowledge Graph', id: 'graph' },
    { icon: UploadCloud, label: 'Ingestion', id: 'ingest' },
    { icon: UserCircle, label: 'Profile', id: 'profile' },
]

export function Shell({ children }: { children: React.ReactNode }) {
    const [activeTab, setActiveTab] = useState('dashboard')
    const [isSidebarOpen, setIsSidebarOpen] = useState(true)

    return (
        <div className="flex h-screen overflow-hidden bg-background text-foreground">
            {/* Sidebar */}
            <motion.aside
                initial={false}
                animate={{ width: isSidebarOpen ? 240 : 80 }}
                className="glass border-r border-white/5 relative z-20 flex flex-col"
            >
                <div className="p-4 flex items-center justify-between h-16 border-b border-white/5">
                    <motion.div
                        animate={{ opacity: isSidebarOpen ? 1 : 0 }}
                        className={cn("font-bold text-xl tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400", !isSidebarOpen && "hidden")}
                    >
                        COGNISPHERE
                    </motion.div>
                    <button
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        className="p-2 hover:bg-white/5 rounded-md transition-colors"
                    >
                        {isSidebarOpen ? <Menu size={20} /> : <Menu size={20} />}
                    </button>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={cn(
                                "w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200 group relative overflow-hidden",
                                activeTab === item.id
                                    ? "bg-primary/20 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)]"
                                    : "hover:bg-white/5 text-muted-foreground hover:text-white"
                            )}
                        >
                            <item.icon size={22} className={cn("transition-transform group-hover:scale-110", activeTab === item.id && "text-primary")} />

                            {isSidebarOpen && (
                                <motion.span
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="text-sm font-medium"
                                >
                                    {item.label}
                                </motion.span>
                            )}

                            {activeTab === item.id && (
                                <motion.div
                                    layoutId="activeTab"
                                    className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-r-full"
                                />
                            )}
                        </button>
                    ))}
                </nav>

                <div className="p-4 border-t border-white/5">
                    <button className="w-full flex items-center gap-3 p-3 rounded-lg text-muted-foreground hover:bg-white/5 hover:text-white transition-colors">
                        <Settings size={22} />
                        {isSidebarOpen && <span>Settings</span>}
                    </button>
                </div>
            </motion.aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto relative">
                {/* Header glass overlay */}
                <div className="sticky top-0 z-10 h-16 glass border-b border-white/5 flex items-center px-6 justify-between backdrop-blur-xl">
                    <h2 className="text-lg font-semibold text-white/90">
                        {navItems.find(i => i.id === activeTab)?.label}
                    </h2>
                    <div className="flex items-center gap-4">
                        <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_10px_#10b981]" />
                        <span className="text-xs text-muted-foreground font-mono">SYSTEM ONLINE</span>
                    </div>
                </div>

                <div className="p-8 max-w-7xl mx-auto">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeTab}
                            initial={{ opacity: 0, y: 20, scale: 0.98 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -20, scale: 0.98 }}
                            transition={{ duration: 0.3, ease: "easeOut" }}
                        >
                            {children}

                            {/* Placeholder Content for Demo */}
                            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                                {[1, 2, 3].map((i) => (
                                    <div key={i} className="glass-card h-48 rounded-2xl p-6 flex flex-col justify-between hover:border-primary/50 transition-colors group cursor-pointer">
                                        <div className="h-10 w-10 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                                            <Layers className="text-muted-foreground group-hover:text-primary transition-colors" />
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-medium text-white">Feature Block {i}</h3>
                                            <p className="text-sm text-muted-foreground mt-1">Premium interactive component with glassmorphism.</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    </AnimatePresence>
                </div>
            </main>
        </div>
    )
}
