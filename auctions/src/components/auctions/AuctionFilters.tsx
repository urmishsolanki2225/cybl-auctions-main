import React, { useState, useEffect } from 'react';
import { publicApi } from '../../api/apiUtils';
import './AuctionFilters.css';

export interface FilterOptions {
  company?: string;
  closingDate?: string;
  distance?: string;
  zipCode?: string;
  categories?: string[];
}

interface Company {
  id: number;
  name: string;
}

interface Category {
  id: number;
  name: string;
  slug: string;
}

interface AuctionFiltersProps {
  filters: FilterOptions;
  onFilterChange: (filters: FilterOptions) => void;
  onClearFilters: () => void;
}

const DISTANCE_OPTIONS = [
  { value: '10', label: '10 miles' },
  { value: '25', label: '25 miles' },
  { value: '50', label: '50 miles' },
  { value: '100', label: '100 miles' },
  { value: '150', label: '150 miles' },
  { value: '250', label: '250 miles' },
];

const AuctionFilters: React.FC<AuctionFiltersProps> = ({
  filters,
  onFilterChange,
  onClearFilters
}) => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const fetchFilterData = async () => {
      try {
        setLoading(true);
        const [companiesResponse, categoriesResponse] = await Promise.all([
          publicApi.getCompanies(),
        ]);
        console.log("companiesResponse", companiesResponse)
        setCompanies(companiesResponse || []);
      } catch (error) {
        console.error('Failed to fetch filter data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFilterData();
  }, []);

  const handleInputChange = (field: keyof FilterOptions, value: string) => {
    onFilterChange({
      ...filters,
      [field]: value || undefined
    });
  };

  const handleCategoryToggle = (categoryId: string) => {
    const currentCategories = filters.categories || [];
    const updatedCategories = currentCategories.includes(categoryId)
      ? currentCategories.filter(id => id !== categoryId)
      : [...currentCategories, categoryId];

    onFilterChange({
      ...filters,
      categories: updatedCategories.length > 0 ? updatedCategories : undefined
    });
  };

  const hasActiveFilters = Object.values(filters).some(value => 
    value && (Array.isArray(value) ? value.length > 0 : true)
  );

  if (loading) {
    return <div className="filters-loading">Loading filters...</div>;
  }

  return (
    <div className="auction-filters">
      <div className="filters-header">
        <h3>Filter Auctions</h3>
        <div className="filters-actions">
          <button 
            className="toggle-filters-btn"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Hide Filters' : 'Show Filters'}
          </button>
          {hasActiveFilters && (
            <button 
              className="clear-all-btn"
              onClick={onClearFilters}
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      <div className={`filters-content ${isExpanded ? 'expanded' : ''}`}>
        <div className="filters-grid">
          {/* Company/Affiliate Filter */}
          <div className="filter-group">
            <label htmlFor="company-select">Affiliate/Company</label>
            <select
              id="company-select"
              value={filters.company || ''}
              onChange={(e) => handleInputChange('company', e.target.value)}
              className="filter-select"
            >
              <option value="">All Companies</option>
              {companies.map(company => (
                <option key={company.id} value={company.id.toString()}>
                  {company.name}
                </option>
              ))}
            </select>
          </div>

          {/* Closing Date Filter */}
          <div className="filter-group">
            <label htmlFor="closing-date">Closing Date</label>
            <input
              id="closing-date"
              type="date"
              value={filters.closingDate || ''}
              onChange={(e) => handleInputChange('closingDate', e.target.value)}
              className="filter-input"
            />
          </div>

          {/* Distance Filter */}
          <div className="filter-group">
            <label htmlFor="distance-select">Distance</label>
            <select
              id="distance-select"
              value={filters.distance || ''}
              onChange={(e) => handleInputChange('distance', e.target.value)}
              className="filter-select"
              disabled={!filters.zipCode}
            >
              <option value="">Select Distance</option>
              {DISTANCE_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Zip Code Filter */}
          <div className="filter-group">
            <label htmlFor="zip-code">From Zip Code</label>
            <input
              id="zip-code"
              type="text"
              placeholder="Enter zip code"
              value={filters.zipCode || ''}
              onChange={(e) => handleInputChange('zipCode', e.target.value)}
              className="filter-input"
              maxLength={10}
            />
            {filters.zipCode && !filters.distance && (
              <small className="filter-hint">Select distance to filter by location</small>
            )}
          </div>
        </div>

       

        {/* Active Filters Summary */}
        {hasActiveFilters && (
          <div className="active-filters">
            <h4>Active Filters:</h4>
            <div className="filter-tags">
              {filters.company && (
                <span className="filter-tag">
                  Company: {companies.find(c => c.id.toString() === filters.company)?.name}
                  <button onClick={() => handleInputChange('company', '')}>×</button>
                </span>
              )}
              {filters.closingDate && (
                <span className="filter-tag">
                  Closing: {filters.closingDate}
                  <button onClick={() => handleInputChange('closingDate', '')}>×</button>
                </span>
              )}
              {filters.distance && filters.zipCode && (
                <span className="filter-tag">
                  Within {filters.distance} miles of {filters.zipCode}
                  <button onClick={() => {
                    onFilterChange({...filters, distance: undefined, zipCode: undefined});
                  }}>×</button>
                </span>
              )}
              
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuctionFilters;