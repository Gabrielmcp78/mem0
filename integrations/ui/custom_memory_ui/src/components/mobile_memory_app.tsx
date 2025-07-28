// Mobile Memory App - PWA-ready mobile interface
// Optimized for touch interactions and mobile accessibility

import React, { useState, useEffect } from 'react';
import { Search, Plus, Menu, X, Brain, Filter, Sort } from 'lucide-react';

// Mobile Memory Card Component
export const MobileMemoryCard = ({ memory, onTap, onLongPress }) => {
  const [isPressed, setIsPressed] = useState(false);
  
  const handleTouchStart = () => setIsPressed(true);
  const handleTouchEnd = () => setIsPressed(false);
  
  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-4 border border-gray-200 dark:border-gray-700 transition-all duration-200 ${
        isPressed ? 'scale-95 shadow-lg' : 'scale-100'
      }`}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onClick={() => onTap(memory)}
      onContextMenu={(e) => {
        e.preventDefault();
        onLongPress(memory);
      }}
      role="button"
      tabIndex={0}
      aria-label={`Memory: ${memory.memory?.substring(0, 50)}...`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {memory.memory || 'Untitled Memory'}
          </p>
          <div className="mt-1 flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
            <span>Score: {memory.score?.toFixed(2) || 'N/A'}</span>
            <span>•</span>
            <span>{new Date(memory.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        
        <div className="ml-2 flex-shrink-0">
          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
        </div>
      </div>
    </div>
  );
};

// Mobile Search Bar
export const MobileSearchBar = ({ onSearch, onFilter, hasFilters }) => {
  const [query, setQuery] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
    setIsExpanded(false);
  };
  
  return (
    <div className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search memories..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
              aria-label="Search memories"
            />
          </div>
          
          <button
            type="button"
            onClick={() => onFilter()}
            className={`p-3 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              hasFilters
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
            }`}
            aria-label="Filter memories"
          >
            <Filter size={18} />
          </button>
        </div>
      </form>
    </div>
  );
};

// Mobile Bottom Navigation
export const MobileBottomNav = ({ currentTab, onTabChange }) => {
  const tabs = [
    { id: 'memories', label: 'Memories', icon: Brain },
    { id: 'search', label: 'Search', icon: Search },
    { id: 'add', label: 'Add', icon: Plus },
    { id: 'menu', label: 'Menu', icon: Menu },
  ];
  
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 safe-area-pb">
      <div className="flex items-center justify-around py-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex flex-col items-center justify-center p-2 min-w-0 flex-1 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              currentTab === tab.id
                ? 'text-blue-600 dark:text-blue-400'
                : 'text-gray-600 dark:text-gray-400'
            }`}
            aria-label={tab.label}
            aria-current={currentTab === tab.id ? 'page' : undefined}
          >
            <tab.icon size={20} />
            <span className="text-xs mt-1 truncate">{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

// Mobile Action Sheet
export const MobileActionSheet = ({ isOpen, onClose, memory, onEdit, onDelete, onShare }) => {
  if (!isOpen) return null;
  
  const actions = [
    { label: 'Edit', action: onEdit, color: 'blue' },
    { label: 'Share', action: onShare, color: 'green' },
    { label: 'Delete', action: onDelete, color: 'red' },
  ];
  
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose}></div>
      <div className="relative bg-white dark:bg-gray-800 rounded-t-lg w-full max-w-md mx-4 mb-4 safe-area-pb">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Memory Actions</h3>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label="Close"
            >
              <X size={20} />
            </button>
          </div>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 truncate">
            {memory?.memory}
          </p>
        </div>
        
        <div className="p-4 space-y-2">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={() => {
                action.action(memory);
                onClose();
              }}
              className={`w-full p-3 text-left rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-${action.color}-500 ${
                action.color === 'red'
                  ? 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900'
                  : action.color === 'blue'
                  ? 'text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900'
                  : 'text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900'
              }`}
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// Mobile Pull to Refresh
export const MobilePullToRefresh = ({ onRefresh, children }) => {
  const [isPulling, setIsPulling] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const [startY, setStartY] = useState(0);
  
  const handleTouchStart = (e) => {
    setStartY(e.touches[0].clientY);
  };
  
  const handleTouchMove = (e) => {
    const currentY = e.touches[0].clientY;
    const distance = currentY - startY;
    
    if (distance > 0 && window.scrollY === 0) {
      e.preventDefault();
      setPullDistance(Math.min(distance, 100));
      setIsPulling(distance > 50);
    }
  };
  
  const handleTouchEnd = () => {
    if (isPulling) {
      onRefresh();
    }
    setPullDistance(0);
    setIsPulling(false);
  };
  
  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="relative"
    >
      {pullDistance > 0 && (
        <div
          className="absolute top-0 left-0 right-0 flex items-center justify-center bg-blue-50 dark:bg-blue-900 transition-all duration-200"
          style={{ height: pullDistance }}
        >
          <div className={`transition-transform ${isPulling ? 'rotate-180' : ''}`}>
            <Search size={20} className="text-blue-600 dark:text-blue-400" />
          </div>
        </div>
      )}
      <div style={{ transform: `translateY(${pullDistance}px)` }}>
        {children}
      </div>
    </div>
  );
};

// Main Mobile App Component
export const MobileMemoryApp = () => {
  const [currentTab, setCurrentTab] = useState('memories');
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [showActionSheet, setShowActionSheet] = useState(false);
  const [hasFilters, setHasFilters] = useState(false);
  
  // Load memories
  const loadMemories = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8765/api/v1/memories/');
      const data = await response.json();
      setMemories(data.memories || data);
    } catch (error) {
      console.error('Failed to load memories:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadMemories();
  }, []);
  
  const handleMemoryTap = (memory) => {
    // Navigate to memory detail view
    console.log('Tapped memory:', memory);
  };
  
  const handleMemoryLongPress = (memory) => {
    setSelectedMemory(memory);
    setShowActionSheet(true);
  };
  
  const handleSearch = async (query) => {
    if (!query.trim()) {
      loadMemories();
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8765/api/v1/memories/filter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setMemories(data.memories || data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleFilter = () => {
    // Open filter modal
    console.log('Open filters');
  };
  
  const handleEdit = (memory) => {
    // Open edit modal
    console.log('Edit memory:', memory);
  };
  
  const handleDelete = async (memory) => {
    try {
      await fetch(`http://localhost:8765/api/v1/memories/${memory.id}`, {
        method: 'DELETE',
      });
      setMemories(memories.filter(m => m.id !== memory.id));
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };
  
  const handleShare = (memory) => {
    if (navigator.share) {
      navigator.share({
        title: 'Memory',
        text: memory.memory,
      });
    } else {
      // Fallback to clipboard
      navigator.clipboard.writeText(memory.memory);
    }
  };
  
  const renderMemories = () => (
    <div className="pb-20">
      <MobileSearchBar
        onSearch={handleSearch}
        onFilter={handleFilter}
        hasFilters={hasFilters}
      />
      
      <MobilePullToRefresh onRefresh={loadMemories}>
        <div className="p-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
            </div>
          ) : (
            <div>
              {memories.map((memory) => (
                <MobileMemoryCard
                  key={memory.id}
                  memory={memory}
                  onTap={handleMemoryTap}
                  onLongPress={handleMemoryLongPress}
                />
              ))}
              
              {memories.length === 0 && (
                <div className="text-center py-12">
                  <Brain size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">No memories found</p>
                </div>
              )}
            </div>
          )}
        </div>
      </MobilePullToRefresh>
    </div>
  );
  
  const renderCurrentTab = () => {
    switch (currentTab) {
      case 'memories':
        return renderMemories();
      case 'search':
        return <div className="p-4 pb-20">Search view coming soon...</div>;
      case 'add':
        return <div className="p-4 pb-20">Add memory view coming soon...</div>;
      case 'menu':
        return <div className="p-4 pb-20">Menu view coming soon...</div>;
      default:
        return renderMemories();
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {renderCurrentTab()}
      
      <MobileBottomNav
        currentTab={currentTab}
        onTabChange={setCurrentTab}
      />
      
      <MobileActionSheet
        isOpen={showActionSheet}
        onClose={() => setShowActionSheet(false)}
        memory={selectedMemory}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onShare={handleShare}
      />
    </div>
  );
};

export default MobileMemoryApp;