/**
 * Reusable Select Component
 */

import { forwardRef } from 'react';
import type { SelectHTMLAttributes } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, className = '', ...props }, ref) => {
    return (
      <div className="input-group">
        {label && (
          <label className="input-label">
            {label}
            {props.required && <span className="required">*</span>}
          </label>
        )}
        <select
          ref={ref}
          className={`select ${error ? 'error' : ''} ${className}`}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && <p className="input-error">{error}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';
