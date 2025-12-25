import { useEffect, useCallback } from 'react';

interface KeyboardNavigationOptions {
  onEnter?: () => void;
  onEscape?: () => void;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  onSpace?: () => void;
  onTab?: (e: KeyboardEvent) => void;
  enabled?: boolean;
}

export const useKeyboardNavigation = (
  elementRef: React.RefObject<HTMLElement>,
  options: KeyboardNavigationOptions = {}
) => {
  const {
    onEnter,
    onEscape,
    onArrowUp,
    onArrowDown,
    onArrowLeft,
    onArrowRight,
    onSpace,
    onTab,
    enabled = true,
  } = options;

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      switch (event.key) {
        case 'Enter':
          if (onEnter) {
            event.preventDefault();
            onEnter();
          }
          break;
        case 'Escape':
          if (onEscape) {
            event.preventDefault();
            onEscape();
          }
          break;
        case 'ArrowUp':
          if (onArrowUp) {
            event.preventDefault();
            onArrowUp();
          }
          break;
        case 'ArrowDown':
          if (onArrowDown) {
            event.preventDefault();
            onArrowDown();
          }
          break;
        case 'ArrowLeft':
          if (onArrowLeft) {
            event.preventDefault();
            onArrowLeft();
          }
          break;
        case 'ArrowRight':
          if (onArrowRight) {
            event.preventDefault();
            onArrowRight();
          }
          break;
        case ' ':
          if (onSpace) {
            event.preventDefault();
            onSpace();
          }
          break;
        case 'Tab':
          if (onTab) {
            onTab(event);
          }
          break;
      }
    },
    [
      enabled,
      onEnter,
      onEscape,
      onArrowUp,
      onArrowDown,
      onArrowLeft,
      onArrowRight,
      onSpace,
      onTab,
    ]
  );

  useEffect(() => {
    const element = elementRef.current;
    if (!element || !enabled) return;

    element.addEventListener('keydown', handleKeyDown);

    return () => {
      element.removeEventListener('keydown', handleKeyDown);
    };
  }, [elementRef, handleKeyDown, enabled]);

  // Helper function to make an element focusable
  const makeFocusable = useCallback((element: HTMLElement) => {
    if (!element.hasAttribute('tabindex')) {
      element.setAttribute('tabindex', '0');
    }
  }, []);

  // Helper function to remove focus from an element
  const removeFocus = useCallback((element: HTMLElement) => {
    element.setAttribute('tabindex', '-1');
  }, []);

  return {
    makeFocusable,
    removeFocus,
  };
};

export default useKeyboardNavigation;
