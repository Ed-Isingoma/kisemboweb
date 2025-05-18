async function logOut(e) {
  e.preventDefault();
  try {
    const response = await fetch('/logout/', {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": getCSRFToken() }
    });
    window.location.reload(true);
  } catch (error) {
    console.error("Logout Error:", error);
    alert("Logout failed");
  }
}

function logoutTrigg(e) {
  e.preventDefault()
  document.querySelector("#logout-overlay").classList.toggle('hidden')
}

function playlistsMenu(e) {
  e.preventDefault()
  const overlay = document.querySelector('#playlists-overlay')
  overlay.classList.toggle('hidden')
  const popup = overlay.querySelector('#popup-menu');
  const rect = e.target.getBoundingClientRect();

  popup.style.top = `${rect.top + window.scrollY + Number(rect.height/1.5)}px`;
  popup.style.left = `${rect.left + window.scrollX}px`;
}

function togglePlaylistsAccord(btn) {
  const content = btn.nextElementSibling;
  const icon    = btn.querySelector('svg');

  document.querySelectorAll('#playlists-accordion .content').forEach(div => {
    if (div !== content) {
      div.style.maxHeight = null;
      div.previousElementSibling.querySelector('svg').classList.remove('rotate-180');
    }
  });

  if (content.style.maxHeight) {
    content.style.maxHeight = null;
    icon.classList.remove('rotate-180');
  } else {
    content.style.maxHeight = content.scrollHeight + 'px';
    icon.classList.add('rotate-180');
  }
}

function getCSRFToken() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    let [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') return value;
  }
  return '';
}

function updateTimeLeft() {
  document.querySelectorAll('.time-left').forEach(element => {
    const expiryDate = new Date(element.dataset.expiry);
    const now = new Date();
    const diff = expiryDate - now;

    if (diff <= 0) {
      element.textContent = 'Expired';
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    element.textContent =
      `${days}d ${hours}h ${minutes}m ${seconds}s left`;
  });
}

updateTimeLeft();
setInterval(updateTimeLeft, 1000);

function toggleLineClamp(event) {
  if (window.innerWidth >= 768) return;
  
  event.stopPropagation();
  
  const image = event.currentTarget;
  const textSpan = image.nextElementSibling?.querySelector('span');
  
  if (textSpan) {
    const isClamped = textSpan.classList.contains('line-clamp-2');
    textSpan.classList.toggle('line-clamp-2', !isClamped);
    textSpan.classList.toggle('line-clamp-none', isClamped);
    
    textSpan.classList.toggle('underline', isClamped);
  }
}

function calculatePrice() {
    const topicSelect = document.getElementById('topic-select');
    const durationUnit = document.getElementById('duration-unit').value;
    const durationAmount = parseFloat(document.getElementById('duration-amount').value) || 0;
  
    if (!topicSelect.value) return;
  
    const selectedOption = topicSelect.options[topicSelect.selectedIndex];
    const unitPrice = parseFloat(selectedOption.dataset[durationUnit]);
    const totalPrice = durationAmount * unitPrice;
    console.log(totalPrice)
    document.getElementById('total-price').textContent =
      `UGX ${totalPrice}`;
};

function openSubscriptionOverlay() {
  document.querySelector('#subscription-overlay').classList.remove('hidden')
  const form = document.getElementById('subscription-form');
  form.reset();
  document.getElementById('total-price').textContent = 'UGX 0';
}

document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('login-overlay');
  const overlayBg = document.getElementById('overlay-bg'); // Translucent background
  const closeOverlay = document.getElementById('close-login-overlay'); // "X" button
  const loginForm = document.getElementById('login-form');
  const signupForm = document.getElementById('signup-form');
  const verificationForm = document.getElementById('verification-form');


  document.querySelectorAll('[data-role="login-signup"]').forEach(button => {
    button.addEventListener('click', () => {
      overlay.classList.remove('hidden');
      loginForm.classList.remove('hidden');
      signupForm.classList.add('hidden');
      verificationForm.classList.add('hidden');
    });
  });

  closeOverlay?.addEventListener('click', () => {
    overlay.classList.add('hidden');
  });

  overlayBg?.addEventListener('click', () => {
    overlay.classList.add('hidden');
  });

  document.getElementById('switch-to-signup')?.addEventListener('click', () => {
    loginForm.classList.add('hidden');
    signupForm.classList.remove('hidden');
  });

  document.getElementById('switch-to-login')?.addEventListener('click', () => {
    signupForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
  });

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    const formObject = {};

    formData.forEach((value, key) => {
      formObject[key] = value;
    });

    const submitButton = loginForm.querySelector('button[type="submit"]');
    const originalHTML = submitButton.innerHTML;

    submitButton.innerHTML = `
      <svg class="animate-spin mx-auto text-white" 
       style="height: 1.25rem; width: 1.25rem" 
       xmlns="http://www.w3.org/2000/svg" 
       fill="none" 
       viewBox="0 0 24 24"
       preserveAspectRatio="xMidYMid meet">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l4-4-4-4v4a8 8 0 00-8 8h4z"></path>
      </svg> `
    submitButton.disabled = true;
    submitButton.classList.add('opacity-50', 'cursor-not-allowed');

    try {
      const response = await fetch('/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(), // Send CSRF token in headers
        },
        body: JSON.stringify(formObject),
      });

      const data = await response.json();
      if (data.success) {
        overlay.classList.add('hidden');
        location.reload();
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      submitButton.innerHTML = originalHTML;
      submitButton.disabled = false;
      submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
  });

  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(signupForm);

    if (formData.get('password') !== formData.get('confirm-password')) {
      alert('Passwords do not match');
      return;
    }

    const submitButton = signupForm.querySelector('button[type="submit"]');
    const originalHTML = submitButton.innerHTML;
    submitButton.innerHTML = `
      <svg class="animate-spin mx-auto text-white" 
       style="height: 1.25rem; width: 1.25rem" 
       xmlns="http://www.w3.org/2000/svg" 
       fill="none" 
       viewBox="0 0 24 24"
       preserveAspectRatio="xMidYMid meet">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l4-4-4-4v4a8 8 0 00-8 8h4z"></path>
    </svg> `;
    submitButton.disabled = true;
    submitButton.classList.add('opacity-50', 'cursor-not-allowed');

    try {
      const response = await fetch('/signup/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken()
        },
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        const email = signupForm.querySelector('input[name="email"]').value;
        verificationForm.querySelector('input[name="email"]').value = email;
        signupForm.classList.add('hidden');
        verificationForm.classList.remove('hidden');
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Signup error:', error);
    } finally {
      submitButton.innerHTML = originalHTML;
      submitButton.disabled = false;
      submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
  });

  verificationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(verificationForm);

    const submitButton = verificationForm.querySelector('button[type="submit"]');
    const originalHTML = submitButton.innerHTML;

    submitButton.innerHTML = `
      <svg class="animate-spin mx-auto text-white" 
       style="height: 1.25rem; width: 1.25rem" 
       xmlns="http://www.w3.org/2000/svg" 
       fill="none" 
       viewBox="0 0 24 24"
       preserveAspectRatio="xMidYMid meet">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l4-4-4-4v4a8 8 0 00-8 8h4z"></path>
    </svg> `;
    submitButton.disabled = true;
    submitButton.classList.add('opacity-50', 'cursor-not-allowed');

    try {
      const response = await fetch('/verify-account/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken()
        },
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        overlay.classList.add('hidden');
        location.reload();
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Verification error:', error);
    } finally {
      submitButton.innerHTML = originalHTML;
      submitButton.disabled = false;
      submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
  });

  // document.querySelectorAll('li[data-topic]').forEach(item => {
  //   item.addEventListener('click', () => {
  //     const topicName = item.dataset.topic;
  //     window.location.href = `?tea=${topicName}`;
  //   });
  // });

  document.querySelectorAll('[data-sugar]').forEach(videoItem => {
    videoItem.addEventListener('click', () => {
      const sugar = videoItem.dataset.sugar;
      const params = new URLSearchParams(window.location.search);
      // Ensure tea parameter remains
      // if (!params.get('tea')) return;
      params.set('sugar', sugar);
      window.location.search = params.toString();
    });
  });

  document.getElementById('subscription-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('subscription-overlay')) {
      e.target.classList.add('hidden');
    }
  });

  document.getElementById('playlists-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('playlists-overlay')) {
      e.target.classList.add('hidden');
    }
  });

  document.getElementById('notification-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('notification-overlay')) {
      e.target.classList.add('hidden');
    }
  });

  document.getElementById('logout-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('logout-overlay')) {
      e.target.classList.add('hidden');
    }
  });

  document.getElementById('subscription-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const topicSelect = document.getElementById('topic-select');
    const durationUnit = document.getElementById('duration-unit');
    const durationAmount = document.getElementById('duration-amount');
    const mobileNumber = document.getElementById('mobile-number');
    const submitBtn = document.querySelector('#subscription-form button[type="submit"]');

    const selectedTopic = topicSelect.options[topicSelect.selectedIndex];
    const topicId = selectedTopic.dataset.id;
    const userId = e.target.dataset.user;

    if (!topicId) {
      alert('Please select a topic');
      return;
    }

    const durationValue = parseFloat(durationAmount.value);
    if (isNaN(durationValue) || durationValue <= 0) {
      alert('Please enter a valid duration amount');
      return
    }

    const mobileRegex = /^07\d{8}$/;
    if (!mobileRegex.test(mobileNumber.value)) {
      alert('Please enter a valid mobile number (07xxxxxxxx)');
      return;
    }

    const subscriptionData = {
      topic_id: topicId,
      user_id: userId,
      duration_unit: durationUnit.value,
      duration_amount: durationValue,
      mobile_number: mobileNumber.value,
    };

    submitBtn.disabled = true;
    const originalHTML = submitBtn.innerHTML;
    submitBtn.innerHTML = `
        <svg class="animate-spin mx-auto text-white" 
        style="height: 1.25rem; width: 1.25rem" 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
        preserveAspectRatio="xMidYMid meet">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l4-4-4-4v4a8 8 0 00-8 8h4z"></path>
    </svg> `;
    submitBtn.classList.add('opacity-50', 'cursor-not-allowed');

    try {
      const response = await fetch('/subscribe/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(subscriptionData),
      });

      const result = await response.json();

      if (response.ok && result.redirect) {
        window.open(result.redirect, '_blank');
        document.getElementById('subscription-overlay').classList.add('hidden')
        document.getElementById('notification-overlay').classList.remove('hidden')
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Subscription error:', error);
      alert('An error occurred during subscription');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalHTML;
      submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
  });
});
