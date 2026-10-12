import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { Dashboard } from './pages/Dashboard';
import { CreateJob } from './pages/CreateJob';
import { AnalysisWorkspace } from './pages/AnalysisWorkspace';
import { JobsList } from './pages/JobsList';
import { ClipLibrary } from './pages/ClipLibrary';
import { ClipDetailPage } from './pages/ClipDetail';
import { StorageSettings } from './pages/StorageSettings';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsAndConditions from './pages/TermsAndConditions';
import CookiePolicy from './pages/CookiePolicy';
import RefundPolicy from './pages/RefundPolicy';
import { NotFound } from './pages/NotFound';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [activeClipId, setActiveClipId] = useState<string | null>(null);

  const handleNavigate = (tab: string, id?: string) => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (tab === 'workspace' && id) {
      setActiveJobId(id);
    } else if (tab === 'detail' && id) {
      setActiveClipId(id);
    }
    setCurrentTab(tab);
  };

  const handleJobCreated = (jobId: string) => {
    setActiveJobId(jobId);
    setCurrentTab('workspace');
  };

  const renderContent = () => {
    switch (currentTab) {
      case 'dashboard':
        return <Dashboard onNavigate={handleNavigate} />;
      case 'create':
        return <CreateJob onJobCreated={handleJobCreated} />;
      case 'workspace':
        return activeJobId ? (
          <AnalysisWorkspace jobId={activeJobId} onNavigate={handleNavigate} />
        ) : (
          <Dashboard onNavigate={handleNavigate} />
        );
      case 'jobs':
        return <JobsList onNavigate={handleNavigate} />;
      case 'library':
        return <ClipLibrary onNavigate={handleNavigate} />;
      case 'detail':
        return activeClipId ? (
          <ClipDetailPage clipId={activeClipId} onNavigate={handleNavigate} />
        ) : (
          <ClipLibrary onNavigate={handleNavigate} />
        );
      case 'storage':
        return <StorageSettings />;
      case 'privacy':
        return <PrivacyPolicy />;
      case 'terms':
        return <TermsAndConditions />;
      case 'cookies':
        return <CookiePolicy />;
      case 'refunds':
        return <RefundPolicy />;
      default:
        return <NotFound onNavigate={handleNavigate} />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
      <Navbar currentTab={currentTab} onNavigate={handleNavigate} />
      <main style={{ flex: 1, paddingTop: '1.5rem' }}>
        {renderContent()}
      </main>
      <Footer onNavigate={handleNavigate} />
    </div>
  );
};

export default App;
