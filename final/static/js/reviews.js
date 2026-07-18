document.addEventListener('DOMContentLoaded', function () {
    // 1. Target Selector References (Unified via querySelector)
    const toggleBtn = document.querySelector('#toggle-review-form-btn');
    const formPanel = document.querySelector('#review-form-panel');
    const reviewForm = document.querySelector('#client-review-form');
    const feedGrid = document.querySelector('#reviews-feed-grid');
    const template = document.querySelector('#review-card-template');


    window.onerror = function(message, source, lineno, colno, error) {
        if (source && source.includes('app.js')) {
            console.warn("Suppressed a lifestyle template break from app.js layout engine:", message);
            return true; // Prevents the global crash from freezing our form event processing!
        }
        return false;
    };

    if (toggleBtn && formPanel) {
        toggleBtn.addEventListener('click', function () {
            formPanel.classList.toggle('d-none');
            
            // Sync button layout text state
            if (formPanel.classList.contains('d-none')) {
                toggleBtn.textContent = 'Write A Review';
            } else {
                toggleBtn.textContent = 'Close Form Panel';
            }
        });
    }

    if (reviewForm) {
        reviewForm.addEventListener('submit', function (e) {
            e.preventDefault();
            
            const ajaxUrl = reviewForm.getAttribute('data-ajax-url') || '/home/reviews/add/ajax/';
            const formData = new FormData();
            
            // 2. Extract input field criteria cleanly using querySelector elements
            const csrfTokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
            const serviceSelect = document.querySelector('#review-item-id');
            const ratingSelect = document.querySelector('#review-rating');
            const commentTextarea = document.querySelector('#review-text');

            if (!serviceSelect || !commentTextarea) {
                alert('CRITICAL UI CONTEXT BREAK: Review elements could not be resolved.');
                return;
            }

            formData.append('csrfmiddlewaretoken', csrfTokenEl ? csrfTokenEl.value : '');
            formData.append('item_id', serviceSelect.value);
            formData.append('rating', ratingSelect ? ratingSelect.value : '5');
            formData.append('comment', commentTextarea.value.trim());

            // 3. Dispatch Form Pipeline Package to Django backend endpoints
            fetch(ajaxUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (template && feedGrid) {
                        const clone = template.content.cloneNode(true);
                        
                        // 4. Populate Document Fragment Nodes
                        clone.querySelector('.user-review-author-name').textContent = data.username;
                        clone.querySelector('.review-tag').textContent = `// ${data.item_title.toUpperCase()}`;
                        clone.querySelector('.review-body').textContent = `"${data.comment}"`;

                        const starsContainer = clone.querySelector('.review-stars');
                        if (starsContainer) {
                            starsContainer.innerHTML = ''; // Wipe formatting residual noise
                            for (let i = 0; i < 5; i++) {
                                const star = document.createElement('i');
                                star.className = i < data.rating ? 'fa-solid fa-star' : 'fa-regular fa-star';
                                starsContainer.appendChild(star);
                            }
                        }

                        // Wipe placeholder layout if it's the very first review card
                        const emptyMsg = document.querySelector('#no-reviews-msg');
                        if (emptyMsg) {
                            emptyMsg.remove();
                        }

                        // Prepend newly initialized card fragment safely at the top of the grid view panel
                        feedGrid.insertBefore(clone, feedGrid.firstChild);
                    }

                    // 5. Reset UI element fields states
                    reviewForm.reset();
                    if (formPanel) formPanel.classList.add('d-none');
                    if (toggleBtn) toggleBtn.textContent = 'Write A Review';
                    
                    alert('Thank you! Your studio review has been posted successfully.');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('AJAX Failure:', error);
                alert('Network operational framework error. Check terminal trace logs.');
            });
        });
    }
});