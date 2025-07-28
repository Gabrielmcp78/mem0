// Enhanced Memory Dashboard - Main Application
// Accessible, responsive, and feature-rich memory management interface

import React, { useState, useEffect, useCallback } from 'react';
import {
  MemoryCard,
  EnhancedSearch,
  DashboardStats,
  Navigation,
  LoadingSpinner,
  ErrorMessage
} from './enhanced_ui_components';

// API Service
class MemoryAPI {
  private baseUrl: string;
  
  constructor(baseUrl = 'http://localhost:18765') {
    this.baseUrl = baseUrl;
  }
  
  async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }
  
  // Memory operations
  async getMemories(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value.toString());
    });
    
    return this.request(`/api/v1/memories/?${params}`);
  }
  
  async searchMemories(query: string, filters = {}) {
    return this.request('/api/v1/memories/filter', {
      method: 'POST',
      body: JSON.stringify({ query, ...filters }),
    });
  }
  
  async createMemory(memory: any) {
    return this.request('/api/v1/memories/', {
      method: 'POST',
      body: JSON.stringify(memory),
    });
  }
  
  async updateMemory(id: string, memory: any) {
    return this.request(`/api/v1/memories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(memory),
    });
  }
  
  async deleteMemory(id: string) {
    return this.request(`/api/v1/memories/${id}`, {
      method: 'DELETE',
    });
  }
  
  async getRelatedMemories(id: string) {
    return this.request(`/api/v1/memories/${id}/related`);
  }
  
  async getStats() {
    return this.request('/api/v1/stats/');
  }
  
  async getApps() {
    return this.request('/api/v1/apps/');
  }
}

// Main Dashboard Component
export const EnhancedMemoryDashboard = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [isDark, setIsDark] = useState(false);
  const [memories, setMemories] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({});
  const [selectedMemory, setSelectedMemory] = useState(null);
  
  const api = new MemoryAPI();
  
  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  // Theme management
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }
  }, []);
  
  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };
  
  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [memoriesData, statsData] = await Promise.all([
        api.getMemories(filters),
        api.getStats()
      ]);
      
      setMemories(memoriesData.memories || memoriesData);
      setStats(statsData);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSearch = async (query: string, searchFilters = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const results = await api.searchMemories(query, { ...filters, ...searchFilters });
      setMemories(results.memories || results);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleMemoryEdit = (memory) => {
    setSelectedMemory(memory);
    // Open edit modal/form
  };
  
  const handleMemoryDelete = async (memory) => {
    if (window.confirm('Are you sure you want to delete this memory?')) {
      try {
        await api.deleteMemory(memory.id);
        setMemories(memories.filter(m => m.id !== memory.id));
      } catch (err) {
        setError(err);
      }
    }
  };
  
  const handleRelatedMemories = async (memory) => {
    try {
      const related = await api.getRelatedMemories(memory.id);
      // Show related memories in a modal or sidebar
      console.log('Related memories:', related);
    } catch (err) {
      setError(err);
    }
  };
  
  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <button
          onClick={loadDashboardData}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Refresh
        </button>
      </div>
      
      <DashboardStats stats={stats} />
      
      {error && <ErrorMessage error={error} onRetry={loadDashboardData} />}
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
        {loading ? (
          <LoadingSpinner text="Loading recent memories..." />
        ) : (
          <div className="space-y-4">
            {memories.slice(0, 5).map((memory) => (
              <div key={memory.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {memory.memory?.substring(0, 100)}...
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {memory.user_id} • {new Date(memory.created_at).toLocaleString()}
                  </p>
                </div>
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                  Score: {memory.score?.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
  
  const renderMemories = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Memories</h1>
        <button
          onClick={() => setSelectedMemory({})}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        >
          Add Memory
        </button>
      </div>
      
      <EnhancedSearch
        onSearch={handleSearch}
        onFilter={setFilters}
        filters={filters}
      />
      
      {error && <ErrorMessage error={error} onRetry={loadDashboardData} />}
      
      {loading ? (
        <LoadingSpinner text="Loading memories..." />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {memories.map((memory) => (
            <MemoryCard
              key={memory.id}
              memory={memory}
              onEdit={handleMemoryEdit}
              onDelete={handleMemoryDelete}
              onRelated={handleRelatedMemories}
            />
          ))}
        </div>
      )}
      
      {memories.length === 0 && !loading && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 text-lg">No memories found</p>
          <p className="text-gray-400 dark:text-gray-500">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
  
  const renderUsers = () => (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Users</h1>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <p className="text-gray-600 dark:text-gray-400">User management coming soon...</p>
      </div>
    </div>
  );
  
  const renderSettings = () => (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Appearance</h3>
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Dark Mode</span>
              <button
                onClick={toggleTheme}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  isDark ? 'bg-blue-600' : 'bg-gray-200'
                }`}
                role="switch"
                aria-checked={isDark}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    isDark ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">API Configuration</h3>
            <p className="text-gray-600 dark:text-gray-400">API settings coming soon...</p>
          </div>
        </div>
      </div>
    </div>
  );
  
  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return renderDashboard();
      case 'memories':
        return renderMemories();
      case 'users':
        return renderUsers();
      case 'settings':
        return renderSettings();
      default:
        return renderDashboard();
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <Navigation
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        isDark={isDark}
        onThemeToggle={toggleTheme}
      />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderCurrentPage()}
      </main>
    </div>
  );
};

export default EnhancedMemoryDashboard;