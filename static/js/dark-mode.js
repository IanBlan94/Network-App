// Function to toggle dark mode
function toggleDarkMode(isDark) {
    // Add or remove the dark-mode class from the body
    if (isDark) {
        document.body.classList.add('dark-mode');
        // Update the label to show what mode you'll switch to if clicked
        document.querySelector('.theme-switch-wrapper .label').textContent = 'Light Mode';
    } else {
        document.body.classList.remove('dark-mode');
        // Update the label to show what mode you'll switch to if clicked
        document.querySelector('.theme-switch-wrapper .label').textContent = 'Dark Mode';
    }
    
    // Save the preference to localStorage
    localStorage.setItem('darkMode', isDark);
}

// When DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the toggle checkbox
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    
    // Check for saved user preference
    const currentTheme = localStorage.getItem('darkMode');
    
    // If preference exists in localStorage
    if (currentTheme !== null) {
        // Update checkbox state
        toggleSwitch.checked = currentTheme === 'true';
        
        // Apply the theme
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