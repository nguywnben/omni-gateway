// Purposeful interface motion powered by the locally vendored Anime.js runtime.

(function initializeMotion() {
    const animeRuntime = window.anime;
    const animate = animeRuntime?.animate;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const activeAnimations = new WeakMap();

    function cancelAnimation(target) {
        const animation = activeAnimations.get(target);
        if (animation && typeof animation.cancel === 'function') {
            animation.cancel();
        }
        activeAnimations.delete(target);
    }

    function clearMotionStyles(target) {
        target.style.removeProperty('opacity');
        target.style.removeProperty('transform');
        target.style.removeProperty('translate');
        target.style.removeProperty('scale');
    }

    function run(target, parameters, options = {}) {
        if (!target) return Promise.resolve();

        cancelAnimation(target);

        if (reducedMotion.matches || typeof animate !== 'function') {
            if (options.cleanup) clearMotionStyles(target);
            return Promise.resolve();
        }

        return new Promise((resolve) => {
            let completed = false;
            const finish = () => {
                if (completed) return;
                completed = true;
                activeAnimations.delete(target);
                if (options.cleanup) clearMotionStyles(target);
                resolve();
            };

            const animation = animate(target, {
                ...parameters,
                onComplete: finish,
            });
            activeAnimations.set(target, animation);
        });
    }

    function enterModal(overlay) {
        const dialog = overlay?.querySelector('.message-modal');
        return Promise.all([
            run(overlay, {
                opacity: {from: 0, to: 1},
                duration: 140,
                ease: 'out(2)',
            }, {cleanup: true}),
            run(dialog, {
                opacity: {from: 0, to: 1},
                y: {from: 6, to: 0},
                scale: {from: 0.992, to: 1},
                duration: 170,
                ease: 'out(3)',
            }, {cleanup: true}),
        ]);
    }

    function exitModal(overlay) {
        const dialog = overlay?.querySelector('.message-modal');
        return Promise.all([
            run(overlay, {
                opacity: {from: 1, to: 0},
                duration: 110,
                ease: 'in(2)',
            }),
            run(dialog, {
                opacity: {from: 1, to: 0},
                y: {from: 0, to: 4},
                scale: {from: 1, to: 0.996},
                duration: 110,
                ease: 'in(2)',
            }),
        ]);
    }

    function enterStatus(status) {
        return run(status, {
            opacity: {from: 0, to: 1},
            y: {from: 6, to: 0},
            duration: 150,
            ease: 'out(3)',
        }, {cleanup: true});
    }

    function exitStatus(status) {
        return run(status, {
            opacity: {from: 1, to: 0},
            y: {from: 0, to: 4},
            duration: 120,
            ease: 'in(2)',
        });
    }

    window.OmniMotion = Object.freeze({
        enterModal,
        exitModal,
        enterStatus,
        exitStatus,
    });
})();
