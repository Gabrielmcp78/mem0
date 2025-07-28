// Enhanced UI Components for Memory Ecosystem
// Modern, accessible, and responsive components

import React, { useState, useEffect } from 'react';
import { Search, Brain, Users, Settings, Moon, Sun, Menu, X } from 'lucide-react';

// Enhanced Memory Card Component
export const MemoryCard = ({ memory, onEdit, onDelete, onRelated }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div 
      className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 border border-gray-200 dark:border-gray-700"
      role="article"
      aria-labelledby={`memory-${memory.id}`}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 
              id={`memory-${memory.id}`}
              className="text-lg font-semibold text-gray-900 dark:text-white mb-2"
            >
              {memory.memory || 'Untitled Memory'}
            </h3>
            <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <span>Score: {memory.score?.toFixed(3) || 'N/A'}</span>
              <span>Created: {new Date(memory.created_at).toLocaleDateString()}</span>
              {memory.user_id && <span>User: {memory.user_id}</span>}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              aria-label={isExpanded ? 'Collapse memory' : 'Expand memory'}
            >
              {isExpanded ? <X size={16} /> : <Menu size={16} />}
            </button>
          </div>
        </div>
        
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => onEdit(memory)}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                aria-label={`Edit memory ${memory.id}`}
              >
                Edit
              </button>
              <button
                onClick={() => onRelated(memory)}
                className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                aria-label={`Find related memories to ${memory.id}`}
              >
                Related
              </button>
              <button
                onClick={() => onDelete(memory)}
                className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                aria-label={`Delete memory ${memory.id}`}
              >
                Delete
              </button>
            </div>
            
            {memory.metadata && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Metadata</h4>
                <pre className="text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded overflow-x-auto">
                  {JSON.stringify(memory.metadata, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Search Component
export const EnhancedSearch = ({ onSearch, onFilter, filters }) => {
  const [query, setQuery] = useState('');
  const [isAdvanced, setIsAdvanced] = useState(false);
  
  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query, filters);
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search memories..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            aria-label="Search memories"
          />
        </div>
        
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setIsAdvanced(!isAdvanced)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline focus:outline-none focus:underline"
            aria-expanded={isAdvanced}
            aria-controls="advanced-filters"
          >
            {isAdvanced ? 'Hide' : 'Show'} Advanced Filters
          </button>
          
          <button
            type="submit"
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Search
          </button>
        </div>
        
        {isAdvanced && (
          <div id="advanced-filters" className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <label htmlFor="user-filter" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                User ID
              </label>
              <input
                id="user-filter"
                type="text"
                value={filters.user_id || ''}
                onChange={(e) => onFilter({ ...filters, user_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Filter by user..."
              />
            </div>
            
            <div>
              <label htmlFor="date-filter" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Date Range
              </label>
              <input
                id="date-filter"
                type="date"
                value={filters.date || ''}
                onChange={(e) => onFilter({ ...filters, date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
            
            <div>
              <label htmlFor="score-filter" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Min Score
              </label>
              <input
                id="score-filter"
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={filters.min_score || ''}
                onChange={(e) => onFilter({ ...filters, min_score: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="0.0"
              />
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

// Dashboard Stats Component
export const DashboardStats = ({ stats }) => {
  const statCards = [
    { label: 'Total Memories', value: stats.total_memories, icon: Brain, color: 'blue' },
    { label: 'Active Users', value: stats.active_users, icon: Users, color: 'green' },
    { label: 'Avg Score', value: stats.avg_score?.toFixed(3), icon: Settings, color: 'purple' },
  ];
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {statCards.map((stat, index) => (
        <div
          key={index}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.label}</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{stat.value || '0'}</p>
            </div>
            <div className={`p-3 rounded-full bg-${stat.color}-100 dark:bg-${stat.color}-900`}>
              <stat.icon className={`h-6 w-6 text-${stat.color}-600 dark:text-${stat.color}-400`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Theme Toggle Component
export const ThemeToggle = ({ isDark, onToggle }) => {
  return (
    <button
      onClick={onToggle}
      className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  );
};

// Navigation Component
export const Navigation = ({ currentPage, onPageChange, isDark, onThemeToggle }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Brain },
    { id: 'memories', label: 'Memories', icon: Search },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];
  
  return (
    <nav className="bg-white dark:bg-gray-800 shadow-md border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900 dark:text-white">
                Memory Ecosystem
              </span>
            </div>
            
            <div className="hidden md:flex space-x-4">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onPageChange(item.id)}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    currentPage === item.id
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                      : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                  aria-current={currentPage === item.id ? 'page' : undefined}
                >
                  <item.icon className="h-4 w-4 mr-2" />
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <ThemeToggle isDark={isDark} onToggle={onThemeToggle} />
          </div>
        </div>
      </div>
    </nav>
  );
};

// Loading Component
export const LoadingSpinner = ({ size = 'md', text = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-8" role="status" aria-live="polite">
      <div className={`animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 ${sizeClasses[size]}`}></div>
      <p className="mt-4 text-gray-600 dark:text-gray-400">{text}</p>
    </div>
  );
};

// Error Component
export const ErrorMessage = ({ error, onRetry }) => {
  return (
    <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-6" role="alert">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <X className="h-5 w-5 text-red-400" />
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
            Something went wrong
          </h3>
          <div className="mt-2 text-sm text-red-700 dark:text-red-300">
            {error.message || 'An unexpected error occurred'}
          </div>
          {onRetry && (
            <div className="mt-4">
              <button
                onClick={onRetry}
                className="bg-red-100 dark:bg-red-800 text-red-800 dark:text-red-200 px-4 py-2 rounded-md text-sm font-medium hover:bg-red-200 dark:hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};