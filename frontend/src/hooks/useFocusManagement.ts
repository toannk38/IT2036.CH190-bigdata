import { useEffect, useRef, useCallback } from 'react';

interface UseFocusManagementOptions {
  restoreFocus?: boolean;
  trapFocus?: boolean;
}

export const useFocusManagement = (
  isOpen: boolean,
  options: UseFocusManagementOptions = {}
) => {
  const { restoreFocus = true, trapFocus = false } = options;
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const containerRef = useRef<HTMLElement>(null);

  // Store the previously focused element when opening
  useEffect(() => {
    if (isOpen && restoreFocus) {
      previousActiveElement.current = document.activeElement as HTMLElement;
    }
  }, [isOpen, restoreFocus]);

  // Restore focus when closing
  useEffect(() => {
    return () => {
      if (restoreFocus && previousActiveElement.current) {
        // Use setTimeout to ensure the element is still in the DOM
        setTimeout(() => {
          previousActiveElement.current?.focus();
        }, 0);
      }
    };
  }, [restoreFocus]);

  // Focus trap implementation
  useEffect(() => {
    if (!isOpen || !trapFocus || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[
      focusableElements.length - 1
    ] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    const handleEscapeKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        // Let parent components handle escape
        e.stopPropagation();
      }
    };

    container.addEventListener('keydown', handleTabKey);
    container.addEventListener('keydown', handleEscapeKey);

    // Focus the first element when opening
    if (firstElement) {
      firstElement.focus();
    }

    return () => {
      container.removeEventListener('keydown', handleTabKey);
      container.removeEventListener('keydown', handleEscapeKey);
    };
  }, [isOpen, trapFocus]);

  const focusFirst = useCallback(() => {
    if (!containerRef.current) return;

    const focusableElements = containerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    firstElement?.focus();
  }, []);

  const focusLast = useCallback(() => {
    if (!containerRef.current) return;

    const focusableElements = containerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const lastElement = focusableElements[
      focusableElements.length - 1
    ] as HTMLElement;
    lastElement?.focus();
  }, []);

  return {
    containerRef,
    focusFirst,
    focusLast,
  };
};

export default useFocusManagement;
