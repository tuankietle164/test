let currentSlide = 0;

function showSlide(index) {
    const slides = document.querySelectorAll('.slides');
    const slider = document.querySelector('.slider');
    const totalSlides = slides.length;

    if (index >= totalSlides) {
        currentSlide = 0;
    } else if (index < 0) {
        currentSlide = totalSlides - 1;
    } else {
        currentSlide = index;
    }

    slider.style.transform = `translateX(-${currentSlide * 100 / totalSlides}%)`;
}

function nextSlide() {
    showSlide(currentSlide + 1);
}

function prevSlide() {
    showSlide(currentSlide - 1);
}


// Xử lý hiển thị sdoor
document.getElementById('newsLink').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('sliderSdoor').style.display = 'flex';
});

// Xử lý đóng sdoor
document.getElementById('closeSdoor').addEventListener('click', function() {
    document.getElementById('sliderSdoor').style.display = 'none';
});

// Đóng sdoor khi nhấp ra ngoài nội dung sdoor
window.addEventListener('click', function(event) {
    if (event.target === document.getElementById('sliderSdoor')) {
        document.getElementById('sliderSdoor').style.display = 'none';
    }
});