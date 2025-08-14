/**
 * Mobile Navigation Handler for Makitox
 * Handles hamburger menu functionality and mobile navigation
 */

class MobileNavigation {
    constructor() {
        this.mobileMenuButton = null;
        this.mobileMenu = null;
        this.isMenuOpen = false;
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupMobileNav());
        } else {
            this.setupMobileNav();
        }
    }

    setupMobileNav() {
        this.mobileMenuButton = document.querySelector('.md\\:hidden button');
        if (!this.mobileMenuButton) {
            console.log('Mobile menu button not found');
            return;
        }

        // Create mobile menu if it doesn't exist
        this.createMobileMenu();
        
        // Add event listeners
        this.mobileMenuButton.addEventListener('click', (e) => this.toggleMenu(e));
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
        
        // Handle escape key
        document.addEventListener('keydown', (e) => this.handleEscapeKey(e));
        
        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
    }

    createMobileMenu() {
        // Check if menu already exists
        if (document.getElementById('mobile-menu')) {
            console.log('Mobile menu already exists');
            return;
        }

        const header = document.querySelector('header nav');
        if (!header) {
            console.log('Header nav not found');
            return;
        }

        // Get desktop navigation links
        const desktopNav = document.querySelector('.hidden.md\\:flex');
        if (!desktopNav) {
            console.log('Desktop nav not found');
            return;
        }

        const navLinks = desktopNav.querySelectorAll('a');
        console.log('Found', navLinks.length, 'navigation links');
        
        // Create mobile menu structure
        this.mobileMenu = document.createElement('div');
        this.mobileMenu.id = 'mobile-menu';
        this.mobileMenu.className = 'md:hidden absolute top-full left-0 right-0 glass-modern border-t border-gray-700 transform transition-all duration-300 opacity-0 -translate-y-4 pointer-events-none z-50 hidden';
        
        const menuContent = document.createElement('div');
        menuContent.className = 'container mx-auto px-6 py-4';
        
        const menuList = document.createElement('nav');
        menuList.className = 'flex flex-col space-y-4';
        
        // Clone navigation links for mobile
        navLinks.forEach(link => {
            const mobileLink = link.cloneNode(true);
            mobileLink.className = 'text-white hover:text-orange-400 transition-colors py-2 border-b border-gray-700 last:border-b-0 touch-target';
            
            // Add click handler to close menu
            mobileLink.addEventListener('click', () => this.closeMenu());
            
            menuList.appendChild(mobileLink);
        });
        
        menuContent.appendChild(menuList);
        this.mobileMenu.appendChild(menuContent);
        header.appendChild(this.mobileMenu);
    }

    toggleMenu(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (this.isMenuOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }

    openMenu() {
        if (!this.mobileMenu) return;
        
        this.isMenuOpen = true;
        this.mobileMenu.classList.remove('hidden', 'opacity-0', '-translate-y-4', 'pointer-events-none');
        this.mobileMenu.classList.add('opacity-100', 'translate-y-0', 'pointer-events-auto');
        
        // Update button icon to X
        this.updateButtonIcon(true);
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Focus first menu item for accessibility
        const firstLink = this.mobileMenu.querySelector('a');
        if (firstLink) {
            setTimeout(() => firstLink.focus(), 100);
        }
    }

    closeMenu() {
        if (!this.mobileMenu) return;
        
        this.isMenuOpen = false;
        this.mobileMenu.classList.add('hidden', 'opacity-0', '-translate-y-4', 'pointer-events-none');
        this.mobileMenu.classList.remove('opacity-100', 'translate-y-0', 'pointer-events-auto');
        
        // Update button icon to hamburger
        this.updateButtonIcon(false);
        
        // Restore body scroll
        document.body.style.overflow = '';
    }

    updateButtonIcon(isOpen) {
        if (!this.mobileMenuButton) return;
        
        const svg = this.mobileMenuButton.querySelector('svg');
        if (!svg) return;
        
        if (isOpen) {
            // X icon
            svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
        } else {
            // Hamburger icon
            svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>';
        }
    }

    handleOutsideClick(e) {
        if (!this.isMenuOpen || !this.mobileMenu) return;
        
        // Close menu if clicking outside of menu and button
        if (!this.mobileMenu.contains(e.target) && !this.mobileMenuButton.contains(e.target)) {
            this.closeMenu();
        }
    }

    handleEscapeKey(e) {
        if (e.key === 'Escape' && this.isMenuOpen) {
            this.closeMenu();
            this.mobileMenuButton.focus();
        }
    }

    handleResize() {
        // Close mobile menu if screen becomes desktop size
        if (window.innerWidth >= 768 && this.isMenuOpen) {
            this.closeMenu();
        }
    }
}

// Initialize mobile navigation
const mobileNav = new MobileNavigation();

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileNavigation;
}