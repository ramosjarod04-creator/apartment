// ============================================
// APARTMENT RESERVATION - JAVASCRIPT
// static/js/script.js
// Atomic Design Principles
// ============================================

// ============================================
// ATOMS - Basic Functions
// ============================================

function autoDismissMessages() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-PH', {
        style: 'currency',
        currency: 'PHP',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount).replace('PHP', '₱');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-PH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

// ============================================
// MOLECULES - Combined Functions
// ============================================

function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (this.classList.contains('confirm-form')) {
                return;
            }
            
            if (!validateForm(this)) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
}

function initDeleteConfirmations() {
    const deleteLinks = document.querySelectorAll('a[href*="/delete/"]');
    
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
}

function initResponsiveNav() {
    const navMenu = document.querySelector('.nav-menu');
    
    if (navMenu && window.innerWidth < 768) {
        const menuToggle = document.createElement('button');
        menuToggle.classList.add('menu-toggle');
        menuToggle.innerHTML = '☰';
        menuToggle.style.cssText = `
            display: none;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
        `;
        
        if (window.innerWidth < 768) {
            menuToggle.style.display = 'block';
            navMenu.style.display = 'none';
        }
        
        menuToggle.addEventListener('click', function() {
            navMenu.style.display = navMenu.style.display === 'none' ? 'flex' : 'none';
        });
        
        document.querySelector('.nav-brand').appendChild(menuToggle);
    }
}

function initReservationCalculator() {
    const monthsInput = document.querySelector('input[name="months"]');
    const apartmentSelect = document.querySelector('select[name="apartment"]');
    
    if (monthsInput && apartmentSelect) {
        function calculateTotal() {
            const months = parseFloat(monthsInput.value) || 0;
            const selectedOption = apartmentSelect.options[apartmentSelect.selectedIndex];
            const priceText = selectedOption.text;
            
            // Extract price from option text if formatted like "Unit 101 - ₱15,000.00/month"
            const priceMatch = priceText.match(/₱([\d,]+\.?\d*)/);
            if (priceMatch) {
                const price = parseFloat(priceMatch[1].replace(/,/g, ''));
                const total = price * months;
                
                let preview = document.querySelector('.reservation-preview');
                if (!preview) {
                    preview = document.createElement('div');
                    preview.classList.add('reservation-preview');
                    preview.style.cssText = `
                        margin-top: 1rem;
                        padding: 1rem;
                        background-color: #f3f4f6;
                        border-radius: 0.5rem;
                    `;
                    monthsInput.parentElement.parentElement.appendChild(preview);
                }
                
                preview.innerHTML = `
                    <h4>Reservation Summary</h4>
                    <p><strong>Monthly Rate:</strong> ${formatCurrency(price)}</p>
                    <p><strong>Duration:</strong> ${months} month(s)</p>
                    <p><strong>Total Amount:</strong> <span style="font-size: 1.5rem; color: var(--primary);">${formatCurrency(total)}</span></p>
                `;
            }
        }
        
        monthsInput.addEventListener('input', calculateTotal);
        apartmentSelect.addEventListener('change', calculateTotal);
        
        // Initial calculation
        calculateTotal();
    }
}

function initImagePreview() {
    const imageInput = document.querySelector('input[type="file"][name="image"]');
    
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    let preview = document.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.classList.add('image-preview');
                        preview.style.cssText = `
                            margin-top: 1rem;
                            max-width: 300px;
                        `;
                        imageInput.parentElement.appendChild(preview);
                    }
                    
                    preview.innerHTML = `
                        <img src="${event.target.result}" alt="Preview" style="width: 100%; border-radius: 0.5rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
                    `;
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
}

function initFilterPersistence() {
    const filterForm = document.querySelector('.filter-form');
    
    if (filterForm) {
        filterForm.addEventListener('submit', function() {
            const formData = new FormData(this);
            const filters = {};
            
            formData.forEach((value, key) => {
                if (value) filters[key] = value;
            });
            
            localStorage.setItem('apartmentFilters', JSON.stringify(filters));
        });
        
        const savedFilters = localStorage.getItem('apartmentFilters');
        if (savedFilters) {
            const filters = JSON.parse(savedFilters);
            
            Object.keys(filters).forEach(key => {
                const input = filterForm.querySelector(`[name="${key}"]`);
                if (input) input.value = filters[key];
            });
        }
    }
}

function initApartmentSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    const apartmentCards = document.querySelectorAll('.apartment-card');
    
    if (searchInput && apartmentCards.length > 0) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const searchTerm = this.value.toLowerCase();
                
                apartmentCards.forEach(card => {
                    const text = card.textContent.toLowerCase();
                    card.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }, 300);
        });
    }
}

// ============================================
// ORGANISMS - Complex Interactions
// ============================================

function animateDashboardStats() {
    const statValues = document.querySelectorAll('.stat-value');
    
    statValues.forEach(stat => {
        const finalValue = stat.textContent;
        const isNumber = !isNaN(parseInt(finalValue));
        
        if (isNumber) {
            const numValue = parseInt(finalValue);
            let currentValue = 0;
            const increment = Math.ceil(numValue / 50);
            const duration = 1000;
            const stepTime = duration / 50;
            
            stat.textContent = '0';
            
            const timer = setInterval(() => {
                currentValue += increment;
                if (currentValue >= numValue) {
                    currentValue = numValue;
                    clearInterval(timer);
                }
                stat.textContent = currentValue;
            }, stepTime);
        }
    });
}

function initApartmentTypeFilter() {
    const typeSelect = document.querySelector('select[name="apartment_type"]');
    const bedroomsInput = document.querySelector('input[name="bedrooms"]');
    
    if (typeSelect && bedroomsInput) {
        typeSelect.addEventListener('change', function() {
            const type = this.value;
            
            // Auto-fill bedrooms based on apartment type
            const bedroomMap = {
                'studio': 0,
                '1br': 1,
                '2br': 2,
                '3br': 3,
                'penthouse': 3
            };
            
            if (bedroomMap[type] !== undefined) {
                bedroomsInput.value = bedroomMap[type];
            }
        });
    }
}

function initDateValidation() {
    const checkInInput = document.querySelector('input[name="check_in"]');
    const checkOutInput = document.querySelector('input[name="check_out"]');
    
    if (checkInInput && checkOutInput) {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        checkInInput.setAttribute('min', today);
        checkOutInput.setAttribute('min', today);
        
        checkInInput.addEventListener('change', function() {
            // Set check-out minimum to check-in date
            checkOutInput.setAttribute('min', this.value);
            
            // If check-out is before check-in, clear it
            if (checkOutInput.value && checkOutInput.value < this.value) {
                checkOutInput.value = '';
            }
        });
        
        checkOutInput.addEventListener('change', function() {
            if (checkInInput.value && this.value < checkInInput.value) {
                alert('Check-out date must be after check-in date');
                this.value = '';
            }
        });
    }
}

function initPriceRangeSlider() {
    const minPriceInput = document.querySelector('input[name="min_price"]');
    const maxPriceInput = document.querySelector('input[name="max_price"]');
    
    if (minPriceInput && maxPriceInput) {
        minPriceInput.addEventListener('input', function() {
            const minValue = parseFloat(this.value);
            const maxValue = parseFloat(maxPriceInput.value);
            
            if (maxValue && minValue > maxValue) {
                this.value = maxValue;
            }
        });
        
        maxPriceInput.addEventListener('input', function() {
            const minValue = parseFloat(minPriceInput.value);
            const maxValue = parseFloat(this.value);
            
            if (minValue && maxValue < minValue) {
                this.value = minValue;
            }
        });
    }
}

function initializeApp() {
    console.log('🏢 Apartment Reservation System Initialized');
    
    // Atoms
    autoDismissMessages();
    
    // Molecules
    initFormValidation();
    initDeleteConfirmations();
    initResponsiveNav();
    initReservationCalculator();
    initImagePreview();
    initFilterPersistence();
    initApartmentSearch();
    
    // Organisms
    if (document.querySelector('.dashboard')) {
        animateDashboardStats();
    }
    
    initApartmentTypeFilter();
    initDateValidation();
    initPriceRangeSlider();
    
    console.log('✅ All components initialized successfully!');
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// ============================================
// EVENT LISTENERS
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

window.addEventListener('resize', debounce(function() {
    initResponsiveNav();
}, 250));

document.addEventListener('input', function(e) {
    if (e.target.matches('input, select, textarea')) {
        e.target.classList.remove('error');
    }
});

document.addEventListener('submit', function(e) {
    const submitBtn = e.target.querySelector('button[type="submit"]');
    if (submitBtn && !submitBtn.classList.contains('loading')) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Processing...';
        
        setTimeout(() => {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 3000);
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + B: Book apartment
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        const bookBtn = document.querySelector('a[href*="reservation/create"]');
        if (bookBtn) window.location.href = bookBtn.href;
    }
    
    // Escape: Go back
    if (e.key === 'Escape') {
        const backBtn = document.querySelector('.btn-outline');
        if (backBtn && backBtn.textContent.includes('Back')) {
            backBtn.click();
        }
    }
});

console.log(' Apartment Reservation System Ready! Press Ctrl+B to book.');