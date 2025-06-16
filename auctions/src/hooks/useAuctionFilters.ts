// src/hooks/useAuctionFilters.ts
import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';

export interface FilterOptions {
  company?: string;
  closingDate?: string;
  distance?: string;
  zipCode?: string;
  categories?: string[];
}

export const useAuctionFilters = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Initialize filters from URL params
  const getFiltersFromUrl = useCallback((): FilterOptions => {
    return {
      company: searchParams.get('company') || undefined,
      closingDate: searchParams.get('closingDate') || undefined,
      distance: searchParams.get('distance') || undefined,
      zipCode: searchParams.get('zipCode') || undefined,
      categories: searchParams.get('categories') 
        ? searchParams.get('categories')!.split(',').filter(Boolean)
        : undefined
    };
  }, [searchParams]);

  const [filters, setFilters] = useState<FilterOptions>(getFiltersFromUrl());

  // Update filters when URL changes (e.g., back/forward navigation)
  useEffect(() => {
    setFilters(getFiltersFromUrl());
  }, [getFiltersFromUrl]);

  // Update URL when filters change
  useEffect(() => {
    const newSearchParams = new URLSearchParams();
    
    if (filters.company) {
      newSearchParams.set('company', filters.company);
    }
    if (filters.closingDate) {
      newSearchParams.set('closingDate', filters.closingDate);
    }
    if (filters.distance) {
      newSearchParams.set('distance', filters.distance);
    }
    if (filters.zipCode) {
      newSearchParams.set('zipCode', filters.zipCode);
    }
    if (filters.categories && filters.categories.length > 0) {
      newSearchParams.set('categories', filters.categories.join(','));
    }

    // Only update URL if params have actually changed
    const currentParams = searchParams.toString();
    const newParams = newSearchParams.toString();
    
    if (currentParams !== newParams) {
      setSearchParams(newSearchParams, { replace: true });
    }
  }, [filters, searchParams, setSearchParams]);

  const updateFilters = useCallback((newFilters: FilterOptions) => {
    setFilters(newFilters);
  }, []);

  const updateSingleFilter = useCallback((key: keyof FilterOptions, value: string | string[] | undefined) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  const clearSingleFilter = useCallback((key: keyof FilterOptions) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      delete newFilters[key];
      return newFilters;
    });
  }, []);

  // Build query string for API calls
  const buildApiQueryString = useCallback((customFilters?: FilterOptions): string => {
    const filtersToUse = customFilters || filters;
    const params = new URLSearchParams();
    
    if (filtersToUse.company) {
      params.append('company_id', filtersToUse.company);
    }
    if (filtersToUse.closingDate) {
      params.append('closing_date', filtersToUse.closingDate);
    }
    if (filtersToUse.distance && filtersToUse.zipCode) {
      params.append('distance_radius', filtersToUse.distance);
      params.append('distance_zip', filtersToUse.zipCode);
    }
    if (filtersToUse.categories && filtersToUse.categories.length > 0) {
      filtersToUse.categories.forEach(cat => params.append('categories', cat));
    }
    
    return params.toString();
  }, [filters]);

  // Check if any filters are active
  const hasActiveFilters = useCallback((): boolean => {
    return Object.values(filters).some(value => 
      value && (Array.isArray(value) ? value.length > 0 : true)
    );
  }, [filters]);

  // Get filter summary for display
  const getFilterSummary = useCallback(() => {
    const summary: string[] = [];
    
    if (filters.company) summary.push('Company');
    if (filters.closingDate) summary.push('Closing Date');
    if (filters.distance && filters.zipCode) summary.push('Distance');
    if (filters.categories && filters.categories.length > 0) {
      summary.push(`${filters.categories.length} Categories`);
    }
    
    return summary;
  }, [filters]);

  return {
    filters,
    updateFilters,
    updateSingleFilter,
    clearFilters,
    clearSingleFilter,
    buildApiQueryString,
    hasActiveFilters: hasActiveFilters(),
    filterSummary: getFilterSummary(),
  };
};