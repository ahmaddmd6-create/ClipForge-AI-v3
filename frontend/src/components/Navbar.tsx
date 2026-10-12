import React from 'react';
import { Film, PlusCircle, ListOrdered, Library, HardDrive } from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  onNavigate: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onNavigate }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Film },
    { id: 'create', label: 'Create clips', icon: PlusCircle, isCta: true },
    { id: 'jobs', label: 'Jobs', icon: ListOrdered },
    { id: 'library', label: 'Clip Library', icon: Library },
    { id: 'storage', label: 'Storage & Settings', icon: HardDrive },
  ];

  return (
    <header style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)' }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 1rem' }}>
        <div 
          onClick={() => onNavigate('dashboard')} 
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', userSelect: 'none' }}
        >
          <div style={{ padding: '0.35rem', backgroundColor: 'var(--text-primary)', color: 'white', borderRadius: 'var(--radius-sm)', display: 'flex' }}>
            <Film size={18} />
          </div>
          <span style={{ fontWeight: 700, fontSize: '1.15rem', letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            ClipForge AI
          </span>
        </div>

        <nav aria-label="Main Navigation" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            
            if (item.isCta) {
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className="btn btn-primary"
                  style={{ fontWeight: 600 }}
                >
                  <Icon size={15} />
                  <span>{item.label}</span>
                </button>
              );
            }

            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.45rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  backgroundColor: isActive ? 'var(--bg-tertiary)' : 'transparent',
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                }}
              >
                <Icon size={15} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
