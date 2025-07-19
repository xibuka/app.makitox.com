/**
 * Form validation and handling for Makitox contact forms
 */

class FormHandler {
    constructor() {
        this.init();
    }

    init() {
        // Initialize form validation when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupFormValidation());
        } else {
            this.setupFormValidation();
        }
    }

    setupFormValidation() {
        const contactForm = document.getElementById('contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
            
            // Real-time validation
            const inputs = contactForm.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldError(input));
            });
        }
    }

    handleFormSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        // Validate all fields
        if (this.validateForm(form)) {
            this.submitForm(form, formData);
        }
    }

    validateForm(form) {
        let isValid = true;
        const fields = ['name', 'email', 'subject', 'message'];
        
        fields.forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field && !this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        let isValid = true;
        let errorMessage = '';

        // Clear previous errors
        this.clearFieldError(field);

        switch (fieldName) {
            case 'name':
                if (!value) {
                    errorMessage = 'Name is required';
                    isValid = false;
                } else if (value.length < 2) {
                    errorMessage = 'Name must be at least 2 characters long';
                    isValid = false;
                } else if (value.length > 100) {
                    errorMessage = 'Name must be less than 100 characters';
                    isValid = false;
                }
                break;

            case 'email':
                if (!value) {
                    errorMessage = 'Email is required';
                    isValid = false;
                } else if (!this.isValidEmail(value)) {
                    errorMessage = 'Please enter a valid email address';
                    isValid = false;
                }
                break;

            case 'subject':
                if (!value) {
                    errorMessage = 'Please select a subject';
                    isValid = false;
                }
                break;

            case 'message':
                if (!value) {
                    errorMessage = 'Message is required';
                    isValid = false;
                } else if (value.length < 10) {
                    errorMessage = 'Message must be at least 10 characters long';
                    isValid = false;
                } else if (value.length > 2000) {
                    errorMessage = 'Message must be less than 2000 characters';
                    isValid = false;
                }
                break;
        }

        if (!isValid) {
            this.showFieldError(field, errorMessage);
        }

        return isValid;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showFieldError(field, message) {
        const errorElement = document.getElementById(`${field.name}-error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
        }
        
        // Add error styling to field
        field.classList.add('border-red-500');
        field.classList.remove('border-gray-600');
    }

    clearFieldError(field) {
        const errorElement = document.getElementById(`${field.name}-error`);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.add('hidden');
        }
        
        // Remove error styling
        field.classList.remove('border-red-500');
        field.classList.add('border-gray-600');
    }

    async submitForm(form, formData) {
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        
        try {
            // Show loading state
            submitButton.textContent = 'Sending...';
            submitButton.disabled = true;
            submitButton.classList.add('opacity-75');

            // Hide any previous success/error messages
            this.hideFormMessages();

            // Simulate form submission (replace with actual endpoint)
            await this.simulateFormSubmission(formData);
            
            // Show success message
            this.showFormSuccess();
            
            // Reset form
            form.reset();
            
        } catch (error) {
            console.error('Form submission error:', error);
            this.showFormError('There was an error sending your message. Please try again or contact us directly at support@makitox.com');
        } finally {
            // Restore button state
            submitButton.textContent = originalButtonText;
            submitButton.disabled = false;
            submitButton.classList.remove('opacity-75');
        }
    }

    async simulateFormSubmission(formData) {
        // In a real application, you would send this to your backend
        // For demonstration, we'll simulate a network request
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Simulate successful submission (90% success rate)
                if (Math.random() > 0.1) {
                    resolve({ success: true });
                } else {
                    reject(new Error('Simulated network error'));
                }
            }, 2000);
        });
    }

    showFormSuccess() {
        const successElement = document.getElementById('form-success');
        if (successElement) {
            successElement.classList.remove('hidden');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                successElement.classList.add('hidden');
            }, 5000);
        }
    }

    showFormError(message) {
        // Create error element if it doesn't exist
        let errorElement = document.getElementById('form-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'form-error';
            errorElement.className = 'text-red-400 text-center mt-4';
            
            const form = document.getElementById('contact-form');
            form.appendChild(errorElement);
        }
        
        errorElement.innerHTML = `
            <svg class="w-6 h-6 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            ${message}
        `;
        errorElement.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorElement.classList.add('hidden');
        }, 5000);
    }

    hideFormMessages() {
        const successElement = document.getElementById('form-success');
        const errorElement = document.getElementById('form-error');
        
        if (successElement) {
            successElement.classList.add('hidden');
        }
        
        if (errorElement) {
            errorElement.classList.add('hidden');
        }
    }
}

// Utility functions for additional features
class FormUtils {
    static sanitizeInput(input) {
        // Basic XSS prevention
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }

    static formatFormData(formData) {
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = this.sanitizeInput(value);
        }
        return data;
    }

    static validateFileUpload(file, maxSize = 5 * 1024 * 1024, allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']) {
        if (file.size > maxSize) {
            return {
                valid: false,
                error: `File size must be less than ${maxSize / (1024 * 1024)}MB`
            };
        }

        if (!allowedTypes.includes(file.type)) {
            return {
                valid: false,
                error: `File type not allowed. Allowed types: ${allowedTypes.join(', ')}`
            };
        }

        return { valid: true };
    }
}

// Analytics helper for form interactions
class FormAnalytics {
    static trackFormStart(formName) {
        // Placeholder for analytics tracking
        console.log(`Form started: ${formName}`);
    }

    static trackFormSubmit(formName, success = true) {
        // Placeholder for analytics tracking
        console.log(`Form ${success ? 'submitted' : 'failed'}: ${formName}`);
    }

    static trackFieldError(fieldName, errorType) {
        // Placeholder for analytics tracking
        console.log(`Field error: ${fieldName} - ${errorType}`);
    }
}

// Initialize form handler when script loads
const formHandler = new FormHandler();

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FormHandler, FormUtils, FormAnalytics };
}