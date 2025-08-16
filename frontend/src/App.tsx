import { TooltipProvider } from '@/components/ui/tooltip';
import { type FC } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';
import { ThemeProvider } from './components/ThemeProvider';
import { FocusModeProvider } from './contexts/FocusModeContext';
import { ScrollToTop } from './components/ScrollToTop';
import { FloatingHelpButton } from './components/FloatingHelpButton';
import { Dashboard } from './pages/Dashboard';
import { ForYouPage } from './pages/ForYouPage';
import { CompanyAnnouncementsPage } from './pages/CompanyAnnouncementsPage';
import { KudosFeedPage } from './pages/KudosFeedPage';
import { EmployeeDirectoryPage } from './pages/EmployeeDirectoryPage';
import { EmployeesPage } from './pages/EmployeesPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import CVUploadPage from './pages/CVUploadPage';
import { CVListPage } from './pages/CVListPage';
import { CVProfilePage } from './pages/CVProfilePage';
import { EditCandidatePage } from './pages/EditCandidatePage';
import { SettingsPage } from './pages/SettingsPage';

const AppRoutes: FC = () => {

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Dashboard />
        }
      />
      <Route
        path="/for-you"
        element={
          <ForYouPage />
        }
      />
      <Route
        path="/announcements"
        element={
          <CompanyAnnouncementsPage />
        }
      />
      <Route
        path="/kudos"
        element={
          <KudosFeedPage />
        }
      />
      <Route
        path="/employees"
        element={
          <EmployeeDirectoryPage />
        }
      />
      <Route
        path="/manage-employees"
        element={
          <EmployeesPage />
        }
      />
      <Route
        path="/projects"
        element={
          <ProjectsPage />
        }
      />
      <Route
        path="/analytics"
        element={
          <AnalyticsPage />
        }
      />
      <Route
        path="/cv-upload"
        element={
          <CVUploadPage />
        }
      />
      <Route
        path="/cv-list"
        element={
          <CVListPage />
        }
      />
      <Route
        path="/cv-profile/:fileId"
        element={
          <CVProfilePage />
        }
      />
      <Route
        path="/edit-candidate/:fileId"
        element={
          <EditCandidatePage />
        }
      />
      <Route
        path="/settings"
        element={
          <SettingsPage />
        }
      />
    </Routes>
  );
};

const App: FC = () => {
  return (
    <ThemeProvider defaultTheme="system" storageKey="nexus-ui-theme">
      <FocusModeProvider>
        <TooltipProvider>
            <BrowserRouter>
              <ScrollToTop />
              <AppRoutes />
              <FloatingHelpButton />
              <Toaster />
            </BrowserRouter>
        </TooltipProvider>
      </FocusModeProvider>
    </ThemeProvider>
  );
};

export default App;
