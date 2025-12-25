import { formatPrice } from './formatters';

// ARIA label generators
export const generateAriaLabel = {
  stockPrice: (symbol: string, price: number) =>
    `Giá cổ phiếu ${symbol}: ${formatPrice(price)}`,

  recommendation: (symbol: string, recommendation: string) =>
    `Khuyến nghị cho ${symbol}: ${recommendation}`,

  alert: (symbol: string, priority: string, message: string) =>
    `Cảnh báo ${priority} cho ${symbol}: ${message}`,

  chart: (title: string, dataPoints: number) =>
    `Biểu đồ ${title} với ${dataPoints} điểm dữ liệu`,

  navigation: (page: string) => `Điều hướng đến trang ${page}`,

  search: (query: string, results: number) =>
    `Tìm kiếm "${query}" có ${results} kết quả`,

  pagination: (currentPage: number, totalPages: number) =>
    `Trang ${currentPage} trong tổng số ${totalPages} trang`,

  loading: (content: string) => `Đang tải ${content}...`,

  error: (content: string) => `Lỗi khi tải ${content}`,
};

// Screen reader announcements
export const announceToScreenReader = (
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
) => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.setAttribute('class', 'sr-only');
  announcement.style.position = 'absolute';
  announcement.style.left = '-10000px';
  announcement.style.width = '1px';
  announcement.style.height = '1px';
  announcement.style.overflow = 'hidden';

  document.body.appendChild(announcement);
  announcement.textContent = message;

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

// Focus management utilities
export const focusUtils = {
  // Get all focusable elements within a container
  getFocusableElements: (container: HTMLElement): HTMLElement[] => {
    const focusableSelectors = [
      'button:not([disabled])',
      '[href]',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]',
    ].join(', ');

    return Array.from(container.querySelectorAll(focusableSelectors));
  },

  // Move focus to next/previous focusable element
  moveFocus: (direction: 'next' | 'previous', container?: HTMLElement) => {
    const activeElement = document.activeElement as HTMLElement;
    const focusableElements = focusUtils.getFocusableElements(
      container || document.body
    );

    const currentIndex = focusableElements.indexOf(activeElement);
    let nextIndex: number;

    if (direction === 'next') {
      nextIndex = currentIndex + 1;
      if (nextIndex >= focusableElements.length) {
        nextIndex = 0; // Wrap to first
      }
    } else {
      nextIndex = currentIndex - 1;
      if (nextIndex < 0) {
        nextIndex = focusableElements.length - 1; // Wrap to last
      }
    }

    focusableElements[nextIndex]?.focus();
  },

  // Check if element is visible and focusable
  isFocusable: (element: HTMLElement): boolean => {
    if (element.hasAttribute('disabled')) return false;
    if (element.getAttribute('tabindex') === '-1') return false;
    if (element.offsetParent === null) return false; // Hidden element

    const style = window.getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden') return false;

    return true;
  },
};

// Color contrast utilities
export const colorUtils = {
  // Get contrast ratio between two colors
  getContrastRatio: (color1: string, color2: string): number => {
    const getLuminance = (color: string): number => {
      // Simplified luminance calculation
      // In a real implementation, you'd want a more robust color parsing
      const rgb = color.match(/\d+/g);
      if (!rgb) return 0;

      const [r, g, b] = rgb.map(Number);
      const rsRGB = r / 255;
      const gsRGB = g / 255;
      const bsRGB = b / 255;

      const rLinear =
        rsRGB <= 0.03928
          ? rsRGB / 12.92
          : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
      const gLinear =
        gsRGB <= 0.03928
          ? gsRGB / 12.92
          : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
      const bLinear =
        bsRGB <= 0.03928
          ? bsRGB / 12.92
          : Math.pow((bsRGB + 0.055) / 1.055, 2.4);

      return 0.2126 * rLinear + 0.7152 * gLinear + 0.0722 * bLinear;
    };

    const lum1 = getLuminance(color1);
    const lum2 = getLuminance(color2);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);

    return (brightest + 0.05) / (darkest + 0.05);
  },

  // Check if color combination meets WCAG AA standards
  meetsWCAGAA: (foreground: string, background: string): boolean => {
    return colorUtils.getContrastRatio(foreground, background) >= 4.5;
  },

  // Check if color combination meets WCAG AAA standards
  meetsWCAGAAA: (foreground: string, background: string): boolean => {
    return colorUtils.getContrastRatio(foreground, background) >= 7;
  },
};

// Keyboard event utilities
export const keyboardUtils = {
  // Check if key combination matches
  isKeyCombo: (
    event: KeyboardEvent,
    key: string,
    modifiers?: {
      ctrl?: boolean;
      alt?: boolean;
      shift?: boolean;
      meta?: boolean;
    }
  ): boolean => {
    if (event.key !== key) return false;

    if (modifiers) {
      if (modifiers.ctrl !== undefined && event.ctrlKey !== modifiers.ctrl)
        return false;
      if (modifiers.alt !== undefined && event.altKey !== modifiers.alt)
        return false;
      if (modifiers.shift !== undefined && event.shiftKey !== modifiers.shift)
        return false;
      if (modifiers.meta !== undefined && event.metaKey !== modifiers.meta)
        return false;
    }

    return true;
  },

  // Common keyboard shortcuts
  shortcuts: {
    isEnter: (event: KeyboardEvent) => event.key === 'Enter',
    isSpace: (event: KeyboardEvent) => event.key === ' ',
    isEscape: (event: KeyboardEvent) => event.key === 'Escape',
    isTab: (event: KeyboardEvent) => event.key === 'Tab',
    isArrowUp: (event: KeyboardEvent) => event.key === 'ArrowUp',
    isArrowDown: (event: KeyboardEvent) => event.key === 'ArrowDown',
    isArrowLeft: (event: KeyboardEvent) => event.key === 'ArrowLeft',
    isArrowRight: (event: KeyboardEvent) => event.key === 'ArrowRight',
    isHome: (event: KeyboardEvent) => event.key === 'Home',
    isEnd: (event: KeyboardEvent) => event.key === 'End',
    isPageUp: (event: KeyboardEvent) => event.key === 'PageUp',
    isPageDown: (event: KeyboardEvent) => event.key === 'PageDown',
  },
};

// ARIA live region utilities
export const liveRegionUtils = {
  // Create a live region for announcements
  createLiveRegion: (
    id: string,
    priority: 'polite' | 'assertive' = 'polite'
  ): HTMLElement => {
    let liveRegion = document.getElementById(id);

    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.id = id;
      liveRegion.setAttribute('aria-live', priority);
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      liveRegion.style.position = 'absolute';
      liveRegion.style.left = '-10000px';
      liveRegion.style.width = '1px';
      liveRegion.style.height = '1px';
      liveRegion.style.overflow = 'hidden';

      document.body.appendChild(liveRegion);
    }

    return liveRegion;
  },

  // Announce message to live region
  announce: (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const liveRegion = liveRegionUtils.createLiveRegion(
      'live-region',
      priority
    );
    liveRegion.textContent = message;
  },
};

export default {
  generateAriaLabel,
  announceToScreenReader,
  focusUtils,
  colorUtils,
  keyboardUtils,
  liveRegionUtils,
};
