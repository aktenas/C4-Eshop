$(document).ready(function () {
    loadNavbar();
    loadFooter();
    setThemeFromStorage();
    setupThemeButton();
    setupNewsSection();
    setupBookingPage();
});


function loadNavbar() {
    $('#global-header').load('components/navbar.html', function () {
        setThemeFromStorage();
    });
}

// loads footer
function loadFooter() {
    $('#global-footer').load('components/footer.html');
}

function setThemeFromStorage() {
    const savedTheme = localStorage.getItem('c4-theme');

    if (savedTheme === 'light') {
        $('body').addClass('light-mode'); 
        $('#theme-toggle-icon').removeClass('fa-sun').addClass('fa-moon');
    } else {
        $('body').removeClass('light-mode');
        $('#theme-toggle-icon').removeClass('fa-moon').addClass('fa-sun');
    }
}

function setupThemeButton() {
    $(document).on('click', '#theme-toggle', function () {
        if ($('body').hasClass('light-mode')) {
            localStorage.setItem('c4-theme', 'dark');
        } else {
            localStorage.setItem('c4-theme', 'light');
        }
        setThemeFromStorage();
    });
}

// --- NEWS API ---
function setupNewsSection() {
    const newsBox = document.querySelector('.api-news-container');
    if (!newsBox) return;

    showDefaultNews(newsBox);
    getConventionNews(newsBox);
}

function showDefaultNews(newsBox) {
    const defaultNews = [
        {
            title: 'Loading convention update',
            text: 'Reading the latest information from the official website.'
        },
        {
            title: 'Loading second update',
            text: 'Reading another update from the official website.'
        }
    ];
    showNewsCards(newsBox, defaultNews);
}

function getConventionNews(newsBox) {
    const websiteUrl = 'https://athenstattooconvention.gr/';
    const apiUrl = 'https://r.jina.ai/' + websiteUrl;
    
    fetch(apiUrl)
        .then(function (response) {
            return response.text();
        })
        .then(function (markdownText) {
            showWebsiteNews(newsBox, markdownText);
        })
        .catch(function () {
            console.log('News API is not available right now.');
        });
}

function showWebsiteNews(newsBox, markdownText) {
    const newsItems = findNewsItemsFromText(markdownText);
    if (newsItems.length === 2) {
        showNewsCards(newsBox, newsItems);
    }
}

function findNewsItemsFromText(websiteText) {
    const lines = websiteText.split('\n');
    const newsItems = [];

    lines.forEach(function (line, row) {
        const title = cleanMarkdownText(line);

        if (line.trim().startsWith('#') && isGoodTitle(title) && newsItems.length < 2) {
            const excerpt = findTextAfterLine(lines, row);
            if (excerpt.length > 5) {
                newsItems.push({
                    title: title,
                    text: excerpt
                });
            }
        }
    });
    return newsItems;
}

function cleanMarkdownText(text) {
    return text.replace(/[#*_`[\]()]/g, '').trim().replace(/\s+/g, ' ');
}

function findTextAfterLine(lines, startRow) {
    for (let i = startRow + 1; i < lines.length; i++) {
        const text = cleanMarkdownText(lines[i]);
        if (isGoodExcerpt(text)) {
            return text;
        }
    }
    return '';
}

if (typeof isGoodTitle !== 'function') {
    function isGoodTitle(text) {
        if (text.length < 6) return false;
        if (text === 'Athens Tattoo Convention' || text === 'Athens Tattoo Convention – Athens Tattoo Convention') return false;
        if (text.toLowerCase().includes('presales')) return false;
        return true;
    }
}

if (typeof isGoodExcerpt !== 'function') {
    function isGoodExcerpt(text) {
        if (text.length < 20) return false;
        if (text.toLowerCase() === 'book now' || text.toLowerCase().includes('skip to content')) return false;
        if (text.includes('https://')) return false;
        return true;
    }
}

function showNewsCards(newsBox, newsItems) {
    newsBox.innerHTML = '';
    newsBox.classList.add('api-news-container-active');

    newsItems.forEach(function (item) {
        const card = document.createElement('div');
        const title = document.createElement('h5');
        const text = document.createElement('p');

        card.className = 'api-news-card';
        title.textContent = item.title;
        text.textContent = item.text;
        text.className = 'text-muted mb-0';
        text.style.fontSize = '0.85rem';

        card.appendChild(title);
        card.appendChild(text);
        newsBox.appendChild(card);
    });
}

// --- BOOKING SYSTEM ---
function setupBookingPage() {
    if ($('.booking-progress').length === 0) return;

    let state = {
        currentStep: 0,
        category: '',
        serviceId: '',
        serviceTitle: '',
        servicePrice: '0.00',
        artist: '',
        time: ''
    };

    const headings = [
        { title: "Select a Service", sub: "Book a tattoo session, piercing, or checkup appointment." },
        { title: "Select Option", sub: "Choose a service." },
        { title: "Select an Artist", sub: "Choose an artist." },
        { title: "Select Date and Time", sub: "Choose an available date and time slot below." },
        { title: "Payment", sub: "Make Payment" },
        { title: "Verify Booking", sub: "Review booking." }
    ];

    function generateStudioTimeSlots(artist) {
        if (artist && String(artist).toLowerCase().trim() === 'monster energy') {
            return [
                { raw: "13:00", display: "01:00 PM" },
                { raw: "15:30", display: "03:30 PM" },
                { raw: "18:00", display: "06:00 PM" }
            ];
        }
        
        return [
            { raw: "13:00", display: "01:00 PM" },
            { raw: "13:30", display: "01:30 PM" },
            { raw: "14:00", display: "02:00 PM" },
            { raw: "14:30", display: "02:30 PM" },
            { raw: "15:00", display: "03:00 PM" },
            { raw: "15:30", display: "03:30 PM" },
            { raw: "16:00", display: "04:00 PM" },
            { raw: "16:30", display: "04:30 PM" },
            { raw: "17:00", display: "05:00 PM" },
            { raw: "17:30", display: "05:30 PM" },
            { raw: "18:00", display: "06:00 PM" },
            { raw: "18:30", display: "06:30 PM" },
            { raw: "19:00", display: "07:00 PM" },
            { raw: "19:30", display: "07:30 PM" },
            { raw: "20:00", display: "08:00 PM" }
        ];
    }

    function fetchAndRenderSlots(dateString) {
        const slotsContainer = document.querySelector('#time-slots-container');
        if (!slotsContainer) return;
        
        slotsContainer.innerHTML = ''; 
        const currentArtist = state.artist || ""; 
        
        const checkUrl = `/home/book/check-slots/?date=${dateString}&artist=${encodeURIComponent(currentArtist)}`;
        
        fetch(checkUrl)
            .then(response => response.json())
            .then(data => {
                const takenSlots = data.taken_slots; 
                const masterSlots = generateStudioTimeSlots(currentArtist);
                
                slotsContainer.innerHTML = ''; 

                masterSlots.forEach(slot => {
                    const isTaken = takenSlots.includes(slot.raw) || takenSlots.includes(slot.display);

                    if (isTaken) {
                        return; 
                    }

                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.style.fontFamily = 'monospace';
                    btn.style.letterSpacing = '0.05em';
                    btn.textContent = slot.display;
                    btn.setAttribute('data-time-display', slot.display);
                    btn.className = 'btn btn-sm btn-outline-danger text-white fw-bold studio-time-slot-btn';

                    slotsContainer.appendChild(btn);
                });
            })
            .catch(err => console.error("Error fetching slots:", err));
    }

    // calendar
    const datePickerEl = document.querySelector('#calendar-date-picker');
    if (datePickerEl) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const tomorrowString = tomorrow.toISOString().split('T')[0];
        
        datePickerEl.min = tomorrowString;
        datePickerEl.value = tomorrowString;
        
        fetchAndRenderSlots(tomorrowString);
    }

    $(document).off('change', '#calendar-date-picker').on('change', '#calendar-date-picker', function() {
        const selectedDate = $(this).val();
        if (!selectedDate) return;

        state.time = ''; 
        fetchAndRenderSlots(selectedDate);
    });

    // Step 0 -> Step 1
    $(document).off('click', '.category-select-btn').on('click', '.category-select-btn', function() {
        const chosenCategory = $(this).attr('data-category') || $(this).data('category') || "";
        state.category = chosenCategory;
    
        $('.service-filterable-card').addClass('d-none');
        $(`.service-filterable-card[data-cat="${state.category}"]`).removeClass('d-none');
        
        const monsterEnergyBtn = document.querySelector('.artist-select-btn[data-art="MONSTER ENERGY"]');
        const oreoBtn = document.querySelector('.artist-select-btn[data-art="OREO"]');
        const rubyRedBtn = document.querySelector('.artist-select-btn[data-art="RUBY RED"]');
        
        const isTattoo = state.category && state.category.toLowerCase().includes('tattoo');

        // 1. Filter Monster Energy
        if (monsterEnergyBtn) {
            const column = monsterEnergyBtn.closest('.col-md-4');
            if (column) {
                if (isTattoo) {
                    column.classList.remove('d-none');
                } else {
                    column.classList.add('d-none');
                }
            }
        }

        // 2. Filter Oreo
        if (oreoBtn) {
            const column = oreoBtn.closest('.col-md-4');
            if (column) {
                if (isTattoo) {
                    column.classList.add('d-none');
                } else {
                    column.classList.remove('d-none');
                }
            }
        }

        // 3. Filter Ruby Red
        if (rubyRedBtn) {
            const column = rubyRedBtn.closest('.col-md-4');
            if (column) {
                if (isTattoo) {
                    column.classList.add('d-none');
                } else {
                    column.classList.remove('d-none');
                }
            }
        }
        
        renderStep(1);
    });

    // Step 1 -> Step 2
    $(document).off('click', '.service-select-btn').on('click', '.service-select-btn', function() {
        state.serviceId = $(this).attr('data-id');
        state.serviceTitle = $(this).attr('data-srv');
        state.servicePrice = $(this).attr('data-price') || "0.00";
        
        const bridgeServiceIdInput = document.querySelector('#id_service_id');
        if (bridgeServiceIdInput) {
            bridgeServiceIdInput.value = state.serviceId;
        }

        const paymentPriceLabel = document.querySelector('.live-payment-price');
        const summarySrvNode = document.querySelector('#summary-srv-node');
        
        if (paymentPriceLabel) paymentPriceLabel.textContent = `€${parseFloat(state.servicePrice).toFixed(2)}`;
        if (summarySrvNode) summarySrvNode.textContent = `${state.serviceTitle} (€${parseFloat(state.servicePrice).toFixed(2)})`;

        const monsterEnergyBtn = document.querySelector('.artist-select-btn[data-art="Monster Energy"]');
        if (monsterEnergyBtn) {
            if (state.category && state.category.toLowerCase().includes('piercing')) {
                monsterEnergyBtn.closest('.studio-card')?.classList.add('d-none'); 
                monsterEnergyBtn.classList.add('d-none');
            } else {
                monsterEnergyBtn.classList.remove('d-none');
            }
        }
        
        renderStep(2);
    });

    // Step 2 -> Step 3 
    $(document).off('click', '.artist-select-btn').on('click', '.artist-select-btn', function() {
        state.artist = $(this).attr('data-art');
        
        const bridgeArtistInput = document.querySelector('#id_artist');
        const summaryArtNode = document.querySelector('#summary-art-node');
        
        if (bridgeArtistInput) bridgeArtistInput.value = state.artist;
        if (summaryArtNode) summaryArtNode.textContent = state.artist;

        const currentSelectedDate = document.querySelector('#calendar-date-picker').value;
        if (currentSelectedDate) {
            fetchAndRenderSlots(currentSelectedDate);
        }
        
        renderStep(3);
    });

    $(document).off('click', '.studio-time-slot-btn').on('click', '.studio-time-slot-btn', function() {
        $('.studio-time-slot-btn').removeClass('btn-danger text-black').addClass('btn-outline-danger text-white');
        $(this).removeClass('btn-outline-danger text-white').addClass('btn-danger text-black');
        
        const pickedTimeStr = $(this).attr('data-time-display');
        const dateVal = document.querySelector('#calendar-date-picker').value;

        const dateObj = new Date(dateVal);
        const formattedDate = dateObj.toLocaleDateString('en-US', { 
            month: 'long', 
            day: 'numeric', 
            year: 'numeric' 
        });

        state.time = `${formattedDate} @ ${pickedTimeStr}`;
    });

    // Step 3 -> Step 4
    $(document).off('click', '#calendar-continue-btn').on('click', '#calendar-continue-btn', function() {
        const dateVal = document.querySelector('#calendar-date-picker').value;

        if (!dateVal || !state.time) {
            alert("SYSTEM ALERT:\nPlease select an available calendar date and click a time slot button window before moving forward.");
            return;
        }
        renderStep(4);
    });

    // Step 4 -> Step 5
    $(document).off('click', '#payment-continue-btn').on('click', '#payment-continue-btn', function() {
        const name = document.querySelector('#payment-name').value.trim();
        const card = document.querySelector('#payment-card').value.trim();
        const expiry = document.querySelector('#payment-expiry').value.trim();
        const cvv = document.querySelector('#payment-cvv').value.trim();

        if (!name || !card || !expiry || !cvv) {
            alert("GATEWAY WARNING:\nPlease input valid authentication card parameters before proceeding.");
            return;
        }

        document.querySelector('#summary-cat-node').textContent = state.category;
        document.querySelector('#summary-time-node').textContent = state.time;

        renderStep(5);
    });

    // Step 5 
    $(document).off('click', '#final-confirm-btn').on('click', '#final-confirm-btn', function(e) {
        e.preventDefault();

        const bridgeNotesInput = document.querySelector('#id_notes');
        if (bridgeNotesInput) {
            bridgeNotesInput.value = `Artist: ${state.artist} | Date: ${state.time}`;
        }

        alert(`BOOKING SUCCESSFUL!\nYour appointment for a ${state.serviceTitle} with ${state.artist} on ${state.time} has been registered to your account.`);
        
        const bookingForm = document.querySelector('#django-booking-bridge');
        if (bookingForm) {
            bookingForm.submit();
        }
    });

    // Back Button
    $(document).off('click', '#booking-back-btn').on('click', '#booking-back-btn', function(e) {
        if (state.currentStep > 0) {
            e.preventDefault();
            renderStep(state.currentStep - 1);
        }
    });

    function renderStep(stepNumber) {
        state.currentStep = stepNumber;
        window.scrollTo({ top: 0, behavior: 'smooth' });

        $('.booking-progress-step').removeClass('is-active');
        $('.booking-progress-step').eq(stepNumber).addClass('is-active');

        $('.booking-step-group').addClass('d-none');
        $(`#step-view-${stepNumber}`).removeClass('d-none');

        document.querySelector('#booking-heading').textContent = headings[stepNumber].title;
        document.querySelector('#booking-subtext').textContent = headings[stepNumber].sub;
    }
}