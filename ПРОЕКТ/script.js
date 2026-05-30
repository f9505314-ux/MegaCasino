/* ── Navbar scroll effect ── */
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
});

/* ── Burger / Mobile menu ── */
const burger = document.getElementById('burger');
const mobileNav = document.getElementById('mobileNav');
burger.addEventListener('click', () => {
  burger.classList.toggle('open');
  mobileNav.classList.toggle('open');
});
// close on link click
mobileNav.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    burger.classList.remove('open');
    mobileNav.classList.remove('open');
  });
});

/* ── Testimonial Carousel ── */
const track = document.getElementById('testimonialTrack');
const slides = track.querySelectorAll('.testimonial-slide');
const dotsContainer = document.getElementById('carouselDots');
let current = 0;

// Build dots
slides.forEach((_, i) => {
  const dot = document.createElement('button');
  dot.classList.add('carousel-dot');
  if (i === 0) dot.classList.add('active');
  dot.setAttribute('aria-label', `Slide ${i + 1}`);
  dot.addEventListener('click', () => goTo(i));
  dotsContainer.appendChild(dot);
});

function updateDots() {
  dotsContainer.querySelectorAll('.carousel-dot').forEach((d, i) => {
    d.classList.toggle('active', i === current);
  });
}
function goTo(index) {
  current = (index + slides.length) % slides.length;
  track.style.transform = `translateX(-${current * 100}%)`;
  updateDots();
}
document.getElementById('prevBtn').addEventListener('click', () => goTo(current - 1));
document.getElementById('nextBtn').addEventListener('click', () => goTo(current + 1));

// Auto-play
setInterval(() => goTo(current + 1), 5000);

/* ── Stats counter animation ── */
function animateCounter(el) {
  const target = parseInt(el.dataset.target);
  const duration = 1800;
  const step = target / (duration / 16);
  let currentVal = 0;
  const timer = setInterval(() => {
    currentVal += step;
    if (currentVal >= target) { currentVal = target; clearInterval(timer); }
    el.textContent = Math.floor(currentVal).toLocaleString();
  }, 16);
}

const statsSection = document.getElementById('stats');
let statsAnimated = false;
const statsObserver = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting && !statsAnimated) {
    statsAnimated = true;
    statsSection.querySelectorAll('.stat-number').forEach(animateCounter);
  }
}, { threshold: 0.3 });
statsObserver.observe(statsSection);

/* ── Contact Form Validation ── */
const form = document.getElementById('contactForm');
const msgBox = document.getElementById('formMsg');

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
function setError(el) { el.classList.add('error'); }
function clearError(el) { el.classList.remove('error'); }

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const name = document.getElementById('fname');
  const email = document.getElementById('femail');
  const subject = document.getElementById('fsubject');
  const message = document.getElementById('fmessage');
  let valid = true;

  [name, email, subject, message].forEach(clearError);
  msgBox.className = 'form-msg';
  msgBox.textContent = '';

  if (!name.value.trim()) { setError(name); valid = false; }
  if (!validateEmail(email.value.trim())) { setError(email); valid = false; }
  if (!subject.value.trim()) { setError(subject); valid = false; }
  if (!message.value.trim()) { setError(message); valid = false; }

  if (!valid) {
    msgBox.textContent = 'Please fill in all fields correctly.';
    msgBox.classList.add('error');
    return;
  }

  // Simulate submission
  msgBox.textContent = 'Your message has been sent! We\'ll get back to you shortly.';
  msgBox.classList.add('success');
  form.reset();
});