// Design system "Precision Prospect" — config Tailwind partagée par tous les écrans.
// Extrait des 6 maquettes statiques pour éviter la duplication (Partie 1 du script).
tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "secondary-container": "#dae2fd",
                "inverse-primary": "#b4c5ff",
                "surface-container": "#e5eeff",
                "primary-container": "#2563eb",
                "secondary-fixed": "#dae2fd",
                "tertiary-container": "#007e37",
                "on-primary-fixed-variant": "#003ea8",
                "on-tertiary": "#ffffff",
                "surface-tint": "#0053db",
                "on-surface-variant": "#434655",
                "tertiary-fixed": "#6bff8f",
                "background": "#f8f9ff",
                "on-error": "#ffffff",
                "inverse-surface": "#213145",
                "on-tertiary-fixed-variant": "#005321",
                "surface-bright": "#f8f9ff",
                "surface": "#f8f9ff",
                "surface-container-low": "#eff4ff",
                "on-primary": "#ffffff",
                "on-secondary-fixed-variant": "#3f465c",
                "secondary": "#565e74",
                "on-tertiary-fixed": "#002109",
                "on-secondary-container": "#5c647a",
                "tertiary": "#006229",
                "on-primary-container": "#eeefff",
                "on-secondary": "#ffffff",
                "on-secondary-fixed": "#131b2e",
                "error-container": "#ffdad6",
                "on-error-container": "#93000a",
                "outline-variant": "#c3c6d7",
                "error": "#ba1a1a",
                "on-primary-fixed": "#00174b",
                "outline": "#737686",
                "primary-fixed": "#dbe1ff",
                "surface-container-lowest": "#ffffff",
                "surface-container-high": "#dce9ff",
                "on-tertiary-container": "#c1ffc5",
                "surface-variant": "#d3e4fe",
                "tertiary-fixed-dim": "#4ae176",
                "secondary-fixed-dim": "#bec6e0",
                "on-surface": "#0b1c30",
                "inverse-on-surface": "#eaf1ff",
                "surface-container-highest": "#d3e4fe",
                "primary-fixed-dim": "#b4c5ff",
                "surface-dim": "#cbdbf5",
                "on-background": "#0b1c30",
                "primary": "#004ac6"
            },
            borderRadius: {
                DEFAULT: "0.125rem",
                lg: "0.25rem",
                xl: "0.5rem",
                full: "0.75rem"
            },
            spacing: {
                gutter: "16px",
                "stack-lg": "32px",
                "stack-md": "16px",
                "stack-sm": "8px",
                "container-padding": "24px",
                unit: "4px"
            },
            fontFamily: {
                "display-lg": ["Inter", "sans-serif"],
                "body-sm": ["Inter", "sans-serif"],
                "headline-md": ["Inter", "sans-serif"],
                "mono-data": ["Inter", "monospace"],
                "headline-sm": ["Inter", "sans-serif"],
                "body-md": ["Inter", "sans-serif"],
                "label-bold": ["Inter", "sans-serif"],
                "body-lg": ["Inter", "sans-serif"]
            },
            fontSize: {
                "display-lg": ["36px", { lineHeight: "44px", letterSpacing: "-0.02em", fontWeight: "700" }],
                "body-sm": ["13px", { lineHeight: "18px", fontWeight: "400" }],
                "headline-md": ["24px", { lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600" }],
                "mono-data": ["14px", { lineHeight: "20px", fontWeight: "500" }],
                "headline-sm": ["20px", { lineHeight: "28px", fontWeight: "600" }],
                "body-md": ["14px", { lineHeight: "20px", fontWeight: "400" }],
                "label-bold": ["12px", { lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "600" }],
                "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }]
            }
        }
    }
};
