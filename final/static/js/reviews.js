document.addEventListener('DOMContentLoaded', function () {
    // grabs the review box
    const toggleBtn = document.querySelector('#toggle-review-form-btn');
    const formPanel = document.querySelector('#review-form-panel');
    const reviewForm = document.querySelector('#client-review-form');
    const feedGrid = document.querySelector('#reviews-feed-grid');
    const template = document.querySelector('#review-card-template');


    window.onerror = function(message, source, lineno, colno, error) {
        if (source && source.includes('app.js')) {
            console.warn("Suppressed an error from app.js layout engine:", message);
            return true;
        }
        return false;
    };

    if (toggleBtn && formPanel) {
        toggleBtn.addEventListener('click', function () {
            // toggle is used as an on/off switch
            formPanel.classList.toggle('d-none');
            
            // button label
            if (formPanel.classList.contains('d-none')) {
                toggleBtn.textContent = 'Write A Review';
            } else {
                toggleBtn.textContent = 'Close Form Panel';
            }
        });
    }

    if (reviewForm) {
        reviewForm.addEventListener('submit', function (e) {
            // click event is interrupted and ajax takes over
            e.preventDefault();
            
            const ajaxUrl = reviewForm.getAttribute('data-ajax-url') || '/home/reviews/add/ajax/';
            const formData = new FormData();
            
            // review inputs 
            const csrfTokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
            const serviceSelect = document.querySelector('#review-item-id');
            const ratingSelect = document.querySelector('#review-rating');
            const commentTextarea = document.querySelector('#review-text');
            // if the review inputs arent foundin html stop
            if (!serviceSelect || !commentTextarea) {
                alert('CRITICAL UI CONTEXT BREAK: Review elements could not be resolved.');
                return;
            }

            //load the data in the form
            formData.append('csrfmiddlewaretoken', csrfTokenEl ? csrfTokenEl.value : '');
            formData.append('item_id', serviceSelect.value);
            formData.append('rating', ratingSelect ? ratingSelect.value : '5');
            formData.append('comment', commentTextarea.value.trim());

            // http request creation with the data collected
            fetch(ajaxUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            // django server response converted to json
            .then(response => response.json())
            .then(data => {
                // if the response is successful the html review is constructed
                if (data.success) {
                    if (template && feedGrid) {
                        const clone = template.content.cloneNode(true);
                        
                        // fill the review card with the data
                        clone.querySelector('.user-review-author-name').textContent = data.username;
                        clone.querySelector('.review-tag').textContent = `// ${data.item_title.toUpperCase()}`;
                        clone.querySelector('.review-body').textContent = `"${data.comment}"`;
                        // review star rating
                        const starsContainer = clone.querySelector('.review-stars');
                        if (starsContainer) {
                            starsContainer.innerHTML = '';
                            for (let i = 0; i < 5; i++) {
                                const star = document.createElement('i');
                                star.className = i < data.rating ? 'fa-solid fa-star' : 'fa-regular fa-star';
                                starsContainer.appendChild(star);
                            }
                        }

                        // no reviews message cleared
                        const emptyMsg = document.querySelector('#no-reviews-msg');
                        if (emptyMsg) {
                            emptyMsg.remove();
                        }

                        // posts the review
                        feedGrid.insertBefore(clone, feedGrid.firstChild);
                    }

                    // reset view
                    reviewForm.reset();
                    if (formPanel) formPanel.classList.add('d-none');
                    if (toggleBtn) toggleBtn.textContent = 'Write A Review';
                    
                    alert('Thank you! Your studio review has been posted successfully.');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            // final error catch
            .catch(error => {
                console.error('AJAX Failure:', error);
                alert('Network operational framework error. Check terminal trace logs.');
            });
        });
    }
});