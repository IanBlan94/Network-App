// Function to toggle dark mode
function toggleDarkMode(isDark) {
    // Add or remove the dark-mode class from both html and body
    if (isDark) {
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');
        document.querySelector('.theme-switch-wrapper .label').textContent = 'Light Mode';
    } else {
        document.documentElement.classList.remove('dark-mode');
        document.body.classList.remove('dark-mode');
        document.querySelector('.theme-switch-wrapper .label').textContent = 'Dark Mode';
    }
    
    // Save the preference to localStorage
    localStorage.setItem('darkMode', isDark);
}

// When DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the toggle checkbox
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    
    if (!toggleSwitch) {
        console.error('Dark mode toggle switch not found');
        return;
    }
    
    // Check for saved user preference
    const currentTheme = localStorage.getItem('darkMode');
    
    // If preference exists in localStorage
    if (currentTheme !== null) {
        // Update checkbox state
        toggleSwitch.checked = currentTheme === 'true';
        
        // Apply the theme again to ensure both html and body have the class
        toggleDarkMode(currentTheme === 'true');
    } else {
        // Check if user prefers dark mode from system settings
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
        
        if (prefersDarkScheme.matches) {
            toggleSwitch.checked = true;
            toggleDarkMode(true);
        }
    }
    
    // Listen for toggle changes
    toggleSwitch.addEventListener('change', function() {
        toggleDarkMode(this.checked);
    });
});