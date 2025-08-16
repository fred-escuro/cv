import { Button } from '@/components/ui/button';
import { useFocusMode } from '@/contexts/FocusModeContext';
import { currentUser } from '@/data/mockData';
import { getTimeBasedGreeting } from '@/lib/utils';
import { 
  Focus, 
  Eye, 
  Home, 
  FolderOpen, 
  Users, 
  BarChart3, 
  Upload,
  FileText,
  Settings
} from 'lucide-react';
import { type FC } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';
import { Profile } from './Profile';
import { GlobalSearch } from './GlobalSearch';
import { NotificationDropdown } from './NotificationDropdown';

export const Header: FC = () => {
  const { isFocusMode, toggleFocusMode } = useFocusMode();
  const location = useLocation();
  const greeting = getTimeBasedGreeting();

  // Core navigation items (most important - always visible)
  const coreNavItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/projects', label: 'Projects', icon: FolderOpen },
    { path: '/cv-list', label: 'CV List', icon: FileText },
    { path: '/cv-upload', label: 'CV Upload', icon: Upload },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/manage-employees', label: 'Employees', icon: Users },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/70">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between">
          {/* Left side - Logo */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
                N
              </div>
              <span className="font-semibold text-lg">Nexus</span>
            </Link>
            <div className="hidden sm:block">
              <span className="text-lg font-medium text-muted-foreground">
                {greeting}, {currentUser.name}! 👋
              </span>
            </div>
          </div>
          {/* Right side - Controls */}
          <div className="flex items-center gap-3">
            <div className="hidden lg:block">
              <GlobalSearch />
            </div>
            {/* Focus Mode Button - Only visible on Dashboard */}
            {location.pathname === '/' && (
              <Button
                variant={isFocusMode ? "default" : "outline"}
                size="sm"
                onClick={toggleFocusMode}
                className="gap-2 h-10"
              >
                {isFocusMode ? <Eye className="h-4 w-4" /> : <Focus className="h-4 w-4" />}
                <span className="hidden sm:inline">
                  {isFocusMode ? 'Exit Focus' : 'Focus Mode'}
                </span>
              </Button>
            )}
            <NotificationDropdown />
            <ThemeToggle />
            <Profile />
          </div>
        </div>
      </header>

      {/* Navigation Bar */}
      <div className="sticky top-16 z-40 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/70">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center py-2">
            {/* Main Navigation - Cleaner with dropdowns */}
            <nav className="flex items-center gap-3">
              {/* Core Items - Always visible */}
              {coreNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary/10 text-primary shadow-sm'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted/60'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="hidden sm:inline">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Mobile greeting */}
      <div className="sm:hidden mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-3 pt-3 border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/70">
        <p className="text-sm text-muted-foreground">
          {greeting}, {currentUser.name}! 👋
        </p>
      </div>
    </>
  );
};
