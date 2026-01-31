import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  History, 
  PlayCircle, 
  Settings,
  MessageSquare,
  X
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', to: '/', icon: LayoutDashboard },
  { name: 'Incidents', to: '/incidents', icon: AlertTriangle },
  { name: 'Remediation History', to: '/remediation', icon: History },
  { name: 'Manual Control', to: '/manual', icon: PlayCircle },
  { name: 'AI Assistant', to: '/chat', icon: MessageSquare },
  { name: 'Configuration', to: '/config', icon: Settings },
];

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        ></div>
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-16 left-0 z-40 h-[calc(100vh-4rem)] w-64
          bg-slate-800 border-r border-slate-700
          transition-transform duration-300 ease-in-out
          lg:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Close button for mobile */}
        <div className="lg:hidden flex justify-end p-4">
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-2 rounded-md"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="px-3 py-4 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.to}
              end={item.to === '/'}
              onClick={() => onClose()}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200
                ${
                  isActive
                    ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/50'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                }`
              }
            >
              <item.icon className="h-5 w-5 mr-3" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* Footer info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700">
          <div className="text-xs text-slate-400">
            <p className="font-medium text-slate-300 mb-1">Platform v1.0</p>
            <p>Auto-Remediation System</p>
            <p className="mt-2">
              <a 
                href="https://github.com/mainulhossain123/infra-autofix-agent" 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-slate-200 transition-colors"
              >
                © 2025 mainulhossain123/infra-autofix-agent
              </a>
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
