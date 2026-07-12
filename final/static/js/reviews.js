document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('toggle-review-form-btn');
    const formPanel = document.getElementById('review-form-panel');
    const reviewForm = document.getElementById('client-review-form');
    const feedGrid = document.getElementById('reviews-feed-grid');
    const template = document.getElementById('review-card-template');

    if (toggleBtn && formPanel) {
        toggleBtn.addEventListener('click', function () {
            formPanel.classList.toggle('d-none');
        });
    }

    if (reviewForm) {
        reviewForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const ajaxUrl = reviewForm.getAttribute('data-ajax-url');
            const formData = new FormData();
            
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
            formData.append('item_id', document.getElementById('review-item-id').value);
            formData.append('rating', document.getElementById('review-rating').value);
            formData.append('comment', document.getElementById('review-text').value);

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
                    const clone = template.content.cloneNode(true);
                    
                    clone.querySelector('.user-review-author-name').textContent = data.username;
                    clone.querySelector('.review-tag').textContent = `// ${data.item_title.toUpperCase()}`;
                    clone.querySelector('.review-body').textContent = `"${data.comment}"`;

                    const starsContainer = clone.querySelector('.review-stars');
                    if (starsContainer) {
                        for (let i = 0; i < 5; i++) {
                            const star = document.createElement('i');
                            star.className = i < data.rating ? 'fa-solid fa-star' : 'fa-regular fa-star';
                            starsContainer.appendChild(star);
                        }
                    }

                    const emptyMsg = document.getElementById('no-reviews-msg');
                    if (emptyMsg) {
                        emptyMsg.remove();
                    }

                    feedGrid.insertBefore(clone, feedGrid.firstChild);
                    reviewForm.reset();
                    formPanel.classList.add('d-none');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => console.error('AJAX Failure:', error));
        });
    }
});