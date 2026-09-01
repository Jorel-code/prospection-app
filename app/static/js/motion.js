/**
 * Precision Prospect — motion.js
 * Compteurs animés (effet "odometer") + révélation au scroll.
 * Zéro dépendance externe, respecte prefers-reduced-motion.
 */

(function () {
    "use strict";

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /**
     * Anime un élément texte de 0 jusqu'à valeurFinale.
     * Réutilisable pour n'importe quel KPI chiffré.
     */
    function animerCompteur(element, valeurFinale, duree = 800) {
        if (prefersReducedMotion) {
            element.textContent = formaterNombre(valeurFinale, element);
            return;
        }
        const debut = performance.now();
        const valeurInitiale = 0;

        function etape(maintenant) {
            const progres = Math.min((maintenant - debut) / duree, 1);
            const easeOut = 1 - Math.pow(1 - progres, 3);
            const valeurCourante = Math.round(valeurInitiale + (valeurFinale - valeurInitiale) * easeOut);
            element.textContent = formaterNombre(valeurCourante, element);
            if (progres < 1) requestAnimationFrame(etape);
        }
        requestAnimationFrame(etape);
    }

    /** Ajoute le suffixe (%, ...) déclaré via data-counter-suffix, et sépare les milliers si demandé. */
    function formaterNombre(valeur, element) {
        const suffixe = element.dataset.counterSuffix || "";
        const separer = element.dataset.counterThousands === "true";
        const texte = separer ? valeur.toLocaleString("fr-FR") : String(valeur);
        return texte + suffixe;
    }

    /** Initialise tous les compteurs présents sur la page ([data-counter-value]) */
    function initCompteurs() {
        document.querySelectorAll("[data-counter-value]").forEach((el) => {
            const valeurFinale = parseFloat(el.dataset.counterValue);
            if (!isNaN(valeurFinale)) {
                animerCompteur(el, valeurFinale);
            }
        });
    }

    /** Révélation au scroll : ajoute .reveal-visible quand l'élément entre dans le viewport */
    function initRevealOnScroll() {
        const elements = document.querySelectorAll(".reveal-on-scroll");
        if (elements.length === 0) return;

        if (prefersReducedMotion || !("IntersectionObserver" in window)) {
            elements.forEach((el) => el.classList.add("reveal-visible"));
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("reveal-visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
        );

        elements.forEach((el) => observer.observe(el));
    }

    document.addEventListener("DOMContentLoaded", () => {
        initCompteurs();
        initRevealOnScroll();
    });

    // Exposé globalement si un template a besoin de relancer un compteur
    // après une mise à jour dynamique (ex: après un fetch AJAX).
    window.animerCompteur = animerCompteur;
})();
