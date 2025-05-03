/**
 * Treatment Navigator JavaScript functionality
 */

// Extract the rating from agent responses
function extractRating(text) {
    // Look for a numeric rating (1-5) in the text
    const ratingRegex = /rating[:\s]+([1-5])(\/5)?|([1-5])(\/5)?[\s]+out of[\s]+5|score[\s]*[:\s]+([1-5])/i;
    const match = text.match(ratingRegex);
    
    if (match) {
        // Return the first captured group that contains a number
        for (let i = 1; i < match.length; i++) {
            if (match[i] && !isNaN(match[i])) {
                return parseInt(match[i]);
            }
        }
    }
    
    // Default to 3 if no rating found
    return 3;
}

// Add a custom filter to Jinja templates
// Note: This must be implemented on the Flask side
document.addEventListener('DOMContentLoaded', function() {
    // Handle custom UI interactions
    
    // Make all treatment cards the same height in each row
    function equalizeCardHeights() {
        const cardGroups = document.querySelectorAll('.accordion-body .row');
        
        cardGroups.forEach(group => {
            const cards = group.querySelectorAll('.card');
            let maxHeight = 0;
            
            // Reset heights first
            cards.forEach(card => {
                card.style.height = 'auto';
                const height = card.offsetHeight;
                maxHeight = Math.max(maxHeight, height);
            });
            
            // Set all cards to the max height
            cards.forEach(card => {
                card.style.height = maxHeight + 'px';
            });
        });
    }
    
    // Run on page load and when accordion items are toggled
    window.addEventListener('load', equalizeCardHeights);
    window.addEventListener('resize', equalizeCardHeights);
    
    const accordionButtons = document.querySelectorAll('.accordion-button');
    if (accordionButtons) {
        accordionButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Wait for accordion animation to complete
                setTimeout(equalizeCardHeights, 350);
            });
        });
    }
    
    // Highlight numbers in the results
    function highlightNumbers() {
        const resultTexts = document.querySelectorAll('.card-body p');
        resultTexts.forEach(element => {
            // Replace numeric values with highlighted versions
            element.innerHTML = element.innerHTML.replace(/\b(\d+(\.\d+)?%?)\b/g, '<span class="badge bg-light text-dark">$1</span>');
        });
    }
    
    // Highlight medical terms in the results
    function highlightMedicalTerms() {
        // This is a simplified example - a real implementation would use a more complete medical term dictionary
        const medicalTerms = [
            'efficacy', 'adverse effects', 'contraindication', 'dosage', 'regimen', 
            'clinical trials', 'pharmacokinetics', 'bioavailability', 'metabolism',
            'half-life', 'comorbidity', 'hypersensitivity', 'immunosuppression'
        ];
        
        const resultTexts = document.querySelectorAll('.card-body p');
        
        resultTexts.forEach(element => {
            let html = element.innerHTML;
            
            medicalTerms.forEach(term => {
                const regex = new RegExp('\\b' + term + '\\b', 'gi');
                html = html.replace(regex, '<span class="text-info">$&</span>');
            });
            
            element.innerHTML = html;
        });
    }
    
    // Initialize tooltips if they exist on the page
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0) {
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }
    
    // Initialize highlighting on results page if it contains treatment analyses
    if (document.querySelector('#treatmentAccordion')) {
        highlightNumbers();
        highlightMedicalTerms();
    }
    
    // Handle print functionality
    const printButton = document.querySelector('.btn-outline-primary[onclick="window.print()"]');
    if (printButton) {
        printButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    }
    
    // Expand all accordions when printing
    if (document.querySelector('#treatmentAccordion')) {
        window.addEventListener('beforeprint', function() {
            const collapsedPanels = document.querySelectorAll('.accordion-collapse.collapse:not(.show)');
            collapsedPanels.forEach(panel => {
                panel.classList.add('show', 'print-show');
            });
        });
        
        window.addEventListener('afterprint', function() {
            const tempExpandedPanels = document.querySelectorAll('.accordion-collapse.print-show');
            tempExpandedPanels.forEach(panel => {
                panel.classList.remove('show', 'print-show');
            });
        });
    }
});