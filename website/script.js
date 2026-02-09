// Navigation & Header Logic
document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');

    // Sticky Header Effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Mobile Menu Toggle
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('nav');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            nav.classList.toggle('active');
        });
    }
});

// Calculator Logic
function syncInput(type, source) {
    const input = document.getElementById(`calc-${type}-input`);
    const range = document.getElementById(`calc-${type}-range`);

    if (source === 'range') {
        input.value = range.value;
    } else {
        range.value = input.value;
    }
    calculateMortar();
}

function calculateMortar() {
    // Get values from inputs (they are synced now, source of truth)
    const length = parseFloat(document.getElementById('calc-length-input').value) || 0;
    const width = parseFloat(document.getElementById('calc-width-input').value) || 0;
    const depth = parseFloat(document.getElementById('calc-depth-input').value) || 0;
    
    // New fields
    const density = parseFloat(document.getElementById('calc-density').value) || 1.8;
    const wastage = parseFloat(document.getElementById('calc-wastage').value) || 0;

    // Calculation: L(m) * W(mm) * D(mm) 
    // Simplified: (L * W * D) / 1000 = Liters
    let liters = (length * width * depth) / 1000;
    
    // Apply wastage
    liters = liters * (1 + (wastage / 100));

    // Calculate weight based on density (kg = l * kg/l)
    const kg = liters * density; 

    // Animate numbers slightly for effect? No, just update.
    document.getElementById('result-liters').innerText = liters.toFixed(2);
    document.getElementById('result-kg').innerText = kg.toFixed(1);
}

// Lightbox Logic
document.addEventListener('DOMContentLoaded', () => {
    const galleryItems = document.querySelectorAll('.gallery-item img');
    const lightbox = document.createElement('div');
    lightbox.id = 'lightbox';
    lightbox.className = 'lightbox hidden';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <span class="lightbox-close">&times;</span>
            <img src="" alt="Zoomed Image">
        </div>
    `;
    document.body.appendChild(lightbox);

    const lightboxImg = lightbox.querySelector('img');
    const closeBtn = lightbox.querySelector('.lightbox-close');

    galleryItems.forEach(img => {
        img.addEventListener('click', () => {
            lightboxImg.src = img.src;
            lightbox.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        });
    });

    const closeLightbox = () => {
        lightbox.classList.add('hidden');
        document.body.style.overflow = '';
    };

    closeBtn.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });

    // Escape key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !lightbox.classList.contains('hidden')) {
            closeLightbox();
        }
    });
});

/* --- Scroll Animation Logic --- */
document.addEventListener('DOMContentLoaded', () => {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
            }
        });
    }, observerOptions);

    // Target generic sections for animation
    // Only animate elements that explicitly have the class 'fade-in-section' to prevent visibility issues on mobile
    const elementsToAnimate = document.querySelectorAll('.fade-in-section');
    
    elementsToAnimate.forEach(section => {
        observer.observe(section);
    });
});

/* --- Accordion Logic --- */
function toggleAccordion(header) {
    const item = header.parentElement;
    item.classList.toggle('active');
    
    const content = item.querySelector('.accordion-content');
    if (item.classList.contains('active')) {
        content.style.maxHeight = content.scrollHeight + 'px';
    } else {
        content.style.maxHeight = 0;
    }
}

