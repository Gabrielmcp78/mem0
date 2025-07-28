import React from 'react';
import EnhancedMemoryDashboard from './components/enhanced_memory_dashboard';
import MobileMemoryApp from './components/mobile_memory_app';
import { useMediaQuery } from './hooks/useMediaQuery';

export default function App() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  
  return (
    <div className="min-h-screen">
      {isMobile ? <MobileMemoryApp /> : <EnhancedMemoryDashboard />}
    </div>
  );
}
