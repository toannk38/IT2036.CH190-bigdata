import { Theme } from '@mui/material/styles';

// Responsive breakpoints
export const breakpoints = {
  mobile: '(max-width: 767px)',
  tablet: '(min-width: 768px) and (max-width: 1023px)',
  desktop: '(min-width: 1024px)',
  tabletAndUp: '(min-width: 768px)',
  mobileAndTablet: '(max-width: 1023px)',
} as const;

// Responsive spacing utilities
export const getResponsiveSpacing = (theme: Theme) => ({
  // Padding utilities
  px: {
    xs: theme.spacing(1), // 8px on mobile
    sm: theme.spacing(2), // 16px on small screens
    md: theme.spacing(3), // 24px on medium screens
    lg: theme.spacing(4), // 32px on large screens
  },
  py: {
    xs: theme.spacing(1),
    sm: theme.spacing(2),
    md: theme.spacing(3),
    lg: theme.spacing(4),
  },
  // Margin utilities
  mx: {
    xs: theme.spacing(1),
    sm: theme.spacing(2),
    md: theme.spacing(3),
    lg: theme.spacing(4),
  },
  my: {
    xs: theme.spacing(1),
    sm: theme.spacing(2),
    md: theme.spacing(3),
    lg: theme.spacing(4),
  },
});

// Responsive grid utilities
export const getResponsiveGrid = () => ({
  container: {
    spacing: {
      xs: 1,
      sm: 2,
      md: 3,
    },
  },
  item: {
    // Common responsive patterns
    fullWidth: { xs: 12 },
    halfOnTablet: { xs: 12, md: 6 },
    thirdOnDesktop: { xs: 12, md: 4 },
    quarterOnDesktop: { xs: 12, sm: 6, lg: 3 },
    twoThirdsOnDesktop: { xs: 12, md: 8 },
    oneThirdOnDesktop: { xs: 12, md: 4 },
  },
});

// Touch target utilities
export const touchTargets = {
  minimum: '44px',
  recommended: '48px',
  comfortable: '56px',
  large: '64px',
};

// Touch target mixins for different component types
export const touchTargetStyles = {
  button: {
    minHeight: touchTargets.minimum,
    minWidth: touchTargets.minimum,
    '@media (max-width: 768px)': {
      minHeight: touchTargets.recommended,
      minWidth: touchTargets.recommended,
    },
  },
  iconButton: {
    minHeight: touchTargets.minimum,
    minWidth: touchTargets.minimum,
    padding: '8px',
    '@media (max-width: 768px)': {
      minHeight: touchTargets.recommended,
      minWidth: touchTargets.recommended,
      padding: '12px',
    },
  },
  listItem: {
    minHeight: touchTargets.minimum,
    '@media (max-width: 768px)': {
      minHeight: touchTargets.recommended,
    },
  },
  menuItem: {
    minHeight: touchTargets.minimum,
    paddingTop: '12px',
    paddingBottom: '12px',
    '@media (max-width: 768px)': {
      minHeight: touchTargets.recommended,
      paddingTop: '16px',
      paddingBottom: '16px',
    },
  },
  chip: {
    minHeight: touchTargets.minimum,
    '& .MuiChip-deleteIcon': {
      minWidth: '24px',
      minHeight: '24px',
    },
    '@media (max-width: 768px)': {
      minHeight: touchTargets.recommended,
      '& .MuiChip-deleteIcon': {
        minWidth: '28px',
        minHeight: '28px',
      },
    },
  },
  tab: {
    minHeight: touchTargets.minimum,
    '@media (max-width: 768px)': {
      minHeight: touchTargets.recommended,
    },
  },
  link: {
    minHeight: touchTargets.minimum,
    display: 'inline-flex',
    alignItems: 'center',
    textDecoration: 'none',
    padding: '8px',
    margin: '-8px',
    borderRadius: '4px',
    '@media (max-width: 768px)': {
      minHeight: touchTargets.recommended,
      padding: '12px',
      margin: '-12px',
    },
  },
};

// Responsive font sizes
export const responsiveFontSizes = {
  h1: {
    fontSize: {
      xs: '1.75rem',
      sm: '2rem',
      md: '2.5rem',
    },
  },
  h2: {
    fontSize: {
      xs: '1.5rem',
      sm: '1.75rem',
      md: '2rem',
    },
  },
  h3: {
    fontSize: {
      xs: '1.25rem',
      sm: '1.5rem',
      md: '1.75rem',
    },
  },
  h4: {
    fontSize: {
      xs: '1.125rem',
      sm: '1.25rem',
      md: '1.5rem',
    },
  },
  body1: {
    fontSize: {
      xs: '0.875rem',
      sm: '1rem',
    },
  },
  body2: {
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
    },
  },
};

// Media query helpers
export const mediaQueries = {
  mobile: `@media ${breakpoints.mobile}`,
  tablet: `@media ${breakpoints.tablet}`,
  desktop: `@media ${breakpoints.desktop}`,
  tabletAndUp: `@media ${breakpoints.tabletAndUp}`,
  mobileAndTablet: `@media ${breakpoints.mobileAndTablet}`,
};

// Responsive container widths
export const containerWidths = {
  xs: '100%',
  sm: '600px',
  md: '960px',
  lg: '1280px',
  xl: '1920px',
};

// Helper function to create responsive styles
export const createResponsiveStyles = (styles: {
  mobile?: Record<string, unknown>;
  tablet?: Record<string, unknown>;
  desktop?: Record<string, unknown>;
}) => ({
  ...styles.mobile,
  [mediaQueries.tablet]: styles.tablet,
  [mediaQueries.desktop]: styles.desktop,
});
