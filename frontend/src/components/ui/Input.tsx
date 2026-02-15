/**
 * Reusable Input Component
 */

import { forwardRef } from 'react';
import type { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = '', ...props }, ref) => {
    return (
      <div className="input-group">
        {label && (
          <label className="input-label">
            {label}
            {props.required && <span className="required">*</span>}
          </label>
        )}
        <input
          ref={ref}
          className={`input ${error ? 'error' : ''} ${className}`}
          {...props}
        />
        {error && <p className="input-error">{error}</p>}
        {helperText && !error && <p className="input-helper">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
