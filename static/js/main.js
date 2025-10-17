// Modern Cost Calculation System JavaScript

// Global variables
let isLoading = false;
let animationDelay = 0;

// Initialize when DOM is ready
$(document).ready(function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    // Clear any existing alerts first
    clearAllAlerts();
    
    initializeSidebar();
    initializeAlerts();
    initializeTooltips();
    initializePopovers();
    initializeFormValidation();
    initializeTheme();
    initializeFullscreen();
    initializeLanguageSelector();
    initializeGlobalSearch();
    initializeAnimations();
    initializeKeyboardShortcuts();
    initializePerformanceOptimizations();
}

// Modern Sidebar Management
function initializeSidebar() {
    const sidebarToggle = $('#sidebarCollapse');
    const sidebar = $('#sidebar');
    const content = $('#content');
    
    sidebarToggle.on('click', function() {
        sidebar.toggleClass('active');
        content.toggleClass('active');
        
        // Save sidebar state
        localStorage.setItem('sidebarCollapsed', sidebar.hasClass('active'));
        
        // Add animation class
        sidebar.addClass('slide-in');
        setTimeout(() => sidebar.removeClass('slide-in'), 300);
    });
    
    // Restore sidebar state
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed) {
        sidebar.addClass('active');
        content.addClass('active');
    }
    
    // Close sidebar on mobile when clicking outside
    $(document).on('click', function(e) {
        if ($(window).width() <= 768) {
            if (!$(e.target).closest('#sidebar, #sidebarCollapse').length) {
                sidebar.removeClass('active');
                content.removeClass('active');
            }
        }
    });
}

// Enhanced Alert System
function initializeAlerts() {
    // Auto-hide alerts with animation
    $('.alert').each(function() {
        const alert = $(this);
        const delay = alert.hasClass('alert-danger') ? 8000 : 5000;
        
        setTimeout(function() {
            alert.fadeOut('slow', function() {
                $(this).remove();
            });
        }, delay);
    });
    
    // Add close button functionality
    $('.alert .btn-close').on('click', function() {
        $(this).closest('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    });
}

// Modern Tooltip System
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            delay: { show: 500, hide: 100 },
            animation: true
        });
    });
}

// Modern Popover System
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            delay: { show: 500, hide: 100 },
            animation: true
        });
    });
}

// Enhanced Form Validation
function initializeFormValidation() {
    $('form').on('submit', function(e) {
        if (isLoading) {
            e.preventDefault();
            return false;
        }
        
        const form = $(this);
        const isValid = validateForm(form);
        
        if (!isValid) {
            e.preventDefault();
            return false;
        }
        
        // Add loading state
        setLoadingState(form, true);
    });
    
    // Real-time validation
    $('input, textarea, select').on('blur', function() {
        validateField($(this));
    });
    
    // Clear validation on input
    $('input, textarea, select').on('input', function() {
        $(this).removeClass('is-invalid');
    });
}

// Form validation functions
function validateForm(form) {
    let isValid = true;
    
    form.find('[required]').each(function() {
        const field = $(this);
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.val();
    const fieldType = field.attr('type') || 'text';
    
    if (field.prop('required') && (!value || value.trim() === '')) {
        field.addClass('is-invalid');
        showFieldError(field, 'This field is required');
        return false;
    }
    
    if (value && containsXSS(value)) {
        field.addClass('is-invalid');
        showFieldError(field, 'Invalid characters detected');
        return false;
    }
    
    // Type-specific validation
    if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            field.addClass('is-invalid');
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    if (fieldType === 'number' && value) {
        if (isNaN(value) || parseFloat(value) < 0) {
            field.addClass('is-invalid');
            showFieldError(field, 'Please enter a valid positive number');
            return false;
        }
    }
    
    field.removeClass('is-invalid');
    hideFieldError(field);
    return true;
}

function showFieldError(field, message) {
    field.siblings('.invalid-feedback').remove();
    field.after(`<div class="invalid-feedback">${sanitizeInput(message)}</div>`);
}

function hideFieldError(field) {
    field.siblings('.invalid-feedback').remove();
}

// XSS Protection
function containsXSS(str) {
    const dangerousPatterns = [
        /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
        /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
        /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi,
        /<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi,
        /<link\b[^<]*(?:(?!<\/link>)<[^<]*)*<\/link>/gi,
        /<meta\b[^<]*(?:(?!<\/meta>)<[^<]*)*<\/meta>/gi,
        /javascript:/gi,
        /on\w+\s*=/gi,
        /<[^>]*>/gi
    ];
    
    return dangerousPatterns.some(pattern => pattern.test(str));
}

// Clear all existing alerts
function clearAllAlerts() {
    $('.alert').remove();
}

// Enhanced utility functions
function showAlert(message, type = 'info', duration = 5000) {
    // Remove existing alerts of the same type to prevent duplicates
    $(`.alert-${type}`).remove();
    
    const alertId = 'alert-' + Date.now();
    const iconMap = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${iconMap[type] || 'info-circle'} me-2"></i>
            ${sanitizeInput(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    $('.container-fluid').prepend(alertHtml);
    
    // Auto-hide
    setTimeout(function() {
        $(`#${alertId}`).fadeOut('slow', function() {
            $(this).remove();
        });
    }, duration);
}

function sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    
    return input
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .replace(/\//g, '&#x2F;');
}

// Loading State Management
function setLoadingState(element, loading) {
    isLoading = loading;
    
    if (loading) {
        element.addClass('loading');
        element.find('button[type="submit"]').prop('disabled', true);
        element.find('button[type="submit"]').html('<i class="fas fa-spinner fa-spin me-2"></i>Loading...');
    } else {
        element.removeClass('loading');
        element.find('button[type="submit"]').prop('disabled', false);
        element.find('button[type="submit"]').html(element.find('button[type="submit"]').data('original-text') || 'Submit');
    }
}

// Enhanced Language Switching
function initializeLanguageSelector() {
    // Language dropdown functionality
    $('[data-language]').on('click', function(e) {
        e.preventDefault();
        const language = $(this).data('language');
        if (language) {
            changeLanguage(language);
        }
    });
}

// Global Search Functionality
function initializeGlobalSearch() {
    const searchInput = $('#global-search');
    const searchResults = $('#search-results');
    
    let searchTimeout;
    
    searchInput.on('input', function() {
        const query = $(this).val().trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            searchResults.removeClass('show').empty();
            return;
        }
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Hide search results when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.search-container').length) {
            searchResults.removeClass('show');
        }
    });
    
    // Show search results on focus
    searchInput.on('focus', function() {
        if ($(this).val().trim().length >= 2) {
            searchResults.addClass('show');
        }
    });
}

function performSearch(query) {
    const searchResults = $('#search-results');
    
    // Mock search results - replace with actual API call
    const mockResults = [
        { type: 'cost', title: 'Office Supplies', description: 'Recent cost entry', url: '/costs' },
        { type: 'tour', title: 'Istanbul Tour', description: 'Tour program', url: '/tour-programs' },
        { type: 'user', title: 'John Doe', description: 'User profile', url: '/users' }
    ];
    
    const filteredResults = mockResults.filter(item => 
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.description.toLowerCase().includes(query.toLowerCase())
    );
    
    if (filteredResults.length === 0) {
        searchResults.html(`
            <div class="p-3 text-center text-muted">
                <i class="fas fa-search mb-2"></i>
                <div>No results found for "${query}"</div>
            </div>
        `);
    } else {
        const resultsHtml = filteredResults.map(result => `
            <a href="${result.url}" class="search-result-item d-block p-3 text-decoration-none">
                <div class="d-flex align-items-center">
                    <div class="search-result-icon me-3">
                        <i class="fas fa-${result.type === 'cost' ? 'receipt' : result.type === 'tour' ? 'plane' : 'user'}"></i>
                    </div>
                    <div>
                        <div class="fw-medium text-primary">${result.title}</div>
                        <small class="text-muted">${result.description}</small>
                    </div>
                </div>
            </a>
        `).join('');
        
        searchResults.html(resultsHtml);
    }
    
    searchResults.addClass('show');
}

function changeLanguage(language) {
    if (!language || !['en', 'tr'].includes(language)) {
        return; // Silent fail
    }
    
    // Get CSRF token
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    
    $.ajax({
        url: '/api/change-language',
        method: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': csrfToken
        },
        data: JSON.stringify({ language: language }),
        success: function(response) {
            if (response.status === 'success') {
                // Update UI elements without page refresh
                updateLanguageUI(language);
            }
        },
        error: function(xhr) {
            console.error('Language change error:', xhr.responseText);
        }
    });
}

// Update UI elements for language change without page refresh
function updateLanguageUI(language) {
    // Update page title
    const titles = {
        'en': 'Cost Calculation System',
        'tr': 'Maliyet Hesaplama Sistemi'
    };
    document.title = titles[language] || titles['en'];
    
    // Update HTML lang attribute
    document.documentElement.lang = language;
    
    // Update active language in dropdown
    $('[data-language]').removeClass('active');
    $(`[data-language="${language}"]`).addClass('active');
    
    // Update language button text
    const languageCodes = {
        'en': 'EN',
        'tr': 'TR'
    };
    $('.language-text').text(languageCodes[language] || 'EN');
    
    // Update breadcrumb text
    const breadcrumbTexts = {
        'en': 'Dashboard',
        'tr': 'Kontrol Paneli'
    };
    $('.breadcrumb-item.active').text(breadcrumbTexts[language] || breadcrumbTexts['en']);
    
    // Update search placeholder
    const searchPlaceholders = {
        'en': 'Search...',
        'tr': 'Ara...'
    };
    $('#global-search').attr('placeholder', searchPlaceholders[language] || searchPlaceholders['en']);
    
    
    // Update page content (basic elements)
    updatePageContent(language);
}

// Update page content elements
function updatePageContent(language) {
    const translations = {
        'en': {
            'dashboard': 'Dashboard',
            'welcome': 'Welcome',
            'total_costs': 'Total Costs',
            'total_tours': 'Total Tours',
            'recent_costs': 'Recent Costs',
            'recent_tours': 'Recent Tours',
            'quick_actions': 'Quick Actions',
            'add_cost': 'Add Cost',
            'add_tour': 'Add Tour',
            'costs': 'Costs',
            'tour_program': 'Tour Program',
            'view': 'View',
            'profile': 'Profile',
            'settings': 'Settings',
            'help': 'Help',
            'logout': 'Logout',
            'add_new_cost': 'Add New Cost',
            'add_new_tour': 'Add New Tour',
            'view_all_costs': 'View All Costs',
            'view_all_tours': 'View All Tours',
            'this_month': 'This Month',
            'last_login': 'Last Login',
            'system_settings': 'System Settings',
            'users': 'Users',
            'language': 'Language',
            'search': 'Search',
            'notifications': 'Notifications',
            'new': 'New',
            'new_cost_added': 'New Cost Added',
            'tour_updated': 'Tour Updated',
            'minutes_ago': 'minutes ago',
            'hour_ago': 'hour ago',
            'view_all_notifications': 'View All Notifications',
            'user': 'User'
        },
        'tr': {
            'dashboard': 'Kontrol Paneli',
            'welcome': 'Hoş Geldiniz',
            'total_costs': 'Toplam Maliyetler',
            'total_tours': 'Toplam Turlar',
            'recent_costs': 'Son Maliyetler',
            'recent_tours': 'Son Turlar',
            'quick_actions': 'Hızlı İşlemler',
            'add_cost': 'Maliyet Ekle',
            'add_tour': 'Tur Ekle',
            'costs': 'Maliyetler',
            'tour_program': 'Tur Programı',
            'view': 'Görüntüle',
            'profile': 'Profil',
            'settings': 'Ayarlar',
            'help': 'Yardım',
            'logout': 'Çıkış',
            'add_new_cost': 'Yeni Maliyet Ekle',
            'add_new_tour': 'Yeni Tur Ekle',
            'view_all_costs': 'Tüm Maliyetleri Görüntüle',
            'view_all_tours': 'Tüm Turları Görüntüle',
            'this_month': 'Bu Ay',
            'last_login': 'Son Giriş',
            'system_settings': 'Sistem Ayarları',
            'users': 'Kullanıcılar',
            'language': 'Dil',
            'search': 'Ara',
            'notifications': 'Bildirimler',
            'new': 'Yeni',
            'new_cost_added': 'Yeni Maliyet Eklendi',
            'tour_updated': 'Tur Güncellendi',
            'minutes_ago': 'dakika önce',
            'hour_ago': 'saat önce',
            'view_all_notifications': 'Tüm Bildirimleri Görüntüle',
            'user': 'Kullanıcı'
        }
    };
    
    const texts = translations[language] || translations['en'];
    
    // Update elements with data-text attributes
    Object.keys(texts).forEach(key => {
        $(`[data-text="${key}"]`).text(texts[key]);
    });
    
    // Update specific elements that might not have data attributes
    $('.text-muted:contains("Last Login")').text(texts.last_login);
    $('.text-muted:contains("This Month")').text(texts.this_month);
}

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    const themeIcon = $('#theme-icon');
    if (theme === 'dark') {
        themeIcon.removeClass('fa-moon').addClass('fa-sun');
    } else {
        themeIcon.removeClass('fa-sun').addClass('fa-moon');
    }
    
    // Add transition effect
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
}

// Fullscreen Management
function initializeFullscreen() {
    // Check if browser is already in fullscreen
    if (document.fullscreenElement || document.webkitFullscreenElement || 
        document.mozFullScreenElement || document.msFullscreenElement) {
        updateFullscreenButton(true);
    }
}

function toggleFullscreen() {
    if (!document.fullscreenElement && !document.webkitFullscreenElement && 
        !document.mozFullScreenElement && !document.msFullscreenElement) {
        enterFullscreen();
    } else {
        exitFullscreen();
    }
}

function enterFullscreen() {
    const element = document.documentElement;
    
    if (element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
    } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    } else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
}

function exitFullscreen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
    } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
    }
}

function updateFullscreenButton(isFullscreen) {
    const icon = $('#fullscreen-toggle i');
    if (isFullscreen) {
        icon.removeClass('fa-expand').addClass('fa-compress');
    } else {
        icon.removeClass('fa-compress').addClass('fa-expand');
    }
}

// Event Listeners
$('#theme-toggle').on('click', function() {
    toggleTheme();
});

$('#fullscreen-toggle').on('click', function() {
    toggleFullscreen();
});

// Listen for fullscreen changes
document.addEventListener('fullscreenchange', function() {
    updateFullscreenButton(!!document.fullscreenElement);
});

document.addEventListener('webkitfullscreenchange', function() {
    updateFullscreenButton(!!document.webkitFullscreenElement);
});

document.addEventListener('mozfullscreenchange', function() {
    updateFullscreenButton(!!document.mozFullScreenElement);
});

document.addEventListener('MSFullscreenChange', function() {
    updateFullscreenButton(!!document.msFullscreenElement);
});

// Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // F11 for fullscreen
        if (event.key === 'F11') {
            event.preventDefault();
            toggleFullscreen();
        }
        
        // Ctrl/Cmd + K for search (if search functionality exists)
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            // Focus search input if it exists
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals/alerts
        if (event.key === 'Escape') {
            // Close any open modals
            $('.modal').modal('hide');
            
            // Close any alerts
            $('.alert').fadeOut('slow', function() {
                $(this).remove();
            });
        }
    });
}

// Animation System
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.card, .stats-card').forEach(el => {
        observer.observe(el);
    });
    
    // Stagger animations
    $('.fade-in').each(function(index) {
        $(this).css('animation-delay', (index * 0.1) + 's');
    });
}

// Performance Optimizations
function initializePerformanceOptimizations() {
    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Debounced resize handler
    let resizeTimeout;
    $(window).on('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Handle responsive changes
            if ($(window).width() <= 768) {
                $('#sidebar').removeClass('active');
                $('#content').removeClass('active');
            }
        }, 250);
    });
}

// Enhanced Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Only show alert for actual errors, not for missing resources
    if (e.error && e.error.name !== 'ChunkLoadError' && e.error.name !== 'Loading chunk') {
        showAlert('An unexpected error occurred. Please refresh the page.', 'danger');
    }
});

// Enhanced AJAX Error Handler
$(document).ajaxError(function(event, xhr, settings, thrownError) {
    console.error('AJAX error:', thrownError);
    // Only show alert for actual network errors, not for expected 400/500 responses
    if (xhr.status === 0 || xhr.status >= 500) {
        showAlert('Network error occurred. Please check your connection.', 'danger');
    }
});

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

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

// Export functions for global use
window.CostCalculationApp = {
    showAlert,
    sanitizeInput,
    formatCurrency,
    formatDate,
    debounce,
    setLoadingState,
    toggleTheme,
    toggleFullscreen,
    changeLanguage
};