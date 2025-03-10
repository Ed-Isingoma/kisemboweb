
async function logOut(e) {
  e.preventDefault();
  try {
    const response = await fetch('/logout/', {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": getCSRFToken() }
    });

    if (!response.ok) throw new Error("Logout request failed");

    const result = await response.json();

    if (result.success) {
      document.cookie = "sessionId=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      document.cookie = "userId=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      window.location.reload(true);
    } else {
      alert("Logout failed.");
    }
  } catch (error) {
    console.error("Logout Error:", error);
    alert("An error occurred during logout.");
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

function calculatePrice() {
  const topicSelect = document.getElementById('topic-select');
  const durationUnit = document.getElementById('duration-unit').value;
  const durationAmount = parseFloat(document.getElementById('duration-amount').value) || 0;

  if (!topicSelect.value) return;

  const selectedOption = topicSelect.options[topicSelect.selectedIndex];
  const unitPrice = parseFloat(selectedOption.dataset[durationUnit]);
  const totalPrice = durationAmount * unitPrice;

  document.getElementById('total-price').textContent =
    `UGX ${totalPrice}`;
};

function openSubscriptionOverlay(){
  document.querySelector('#subscription-overlay').classList.remove('hidden')
  const form = document.getElementById('subscription-form');
  form.reset();
  document.getElementById('total-price').textContent = 'UGX 0';
}

document.addEventListener('DOMContentLoaded', () => {
  const accountDropdown = document.getElementById('account-dropdown');
  const dropdownMenu = document.getElementById('dropdown-menu');
  const overlay = document.getElementById('overlay');
  const overlayBg = document.getElementById('overlay-bg'); // Translucent background
  const closeOverlay = document.getElementById('close-overlay'); // "X" button
  const loginForm = document.getElementById('login-form');
  const signupForm = document.getElementById('signup-form');
  const verificationForm = document.getElementById('verification-form');

  accountDropdown.addEventListener('click', () => {
    dropdownMenu.classList.toggle('hidden');
  });

  document.getElementById('login-signup')?.addEventListener('click', () => {
    overlay.classList.remove('hidden');
    loginForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
    verificationForm.classList.add('hidden');
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

    try {
      const response = await fetch('/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(), // Send CSRF token in headers
        },
        body: JSON.stringify(formObject)
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
    }
  });

  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(signupForm);
    if (formData.get('password') !== formData.get('confirm-password')) {
      alert('Passwords do not match');
      return;
    }
    try {
      const response = await fetch('/signup/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken()
        },
        body: formData
      });
      const data = await response.json();
      if (data.success) {
        signupForm.classList.add('hidden');
        verificationForm.classList.remove('hidden');
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Signup error:', error);
    }
  });

  verificationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(verificationForm);
    try {
      const response = await fetch('/verify-account/', {
        method: 'POST',
        body: formData
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
    }
  });

  document.querySelectorAll('li[data-topic]').forEach(item => {
    item.addEventListener('click', () => {
      const topicName = item.dataset.topic;
      window.location.href = `?tea=${topicName}`;
    });
  });

  document.querySelectorAll('[data-sugar]').forEach(videoItem => {
    videoItem.addEventListener('click', () => {
      const sugar = videoItem.dataset.sugar;
      const params = new URLSearchParams(window.location.search);
      // Ensure tea parameter remains
      if (!params.get('tea')) return;
      params.set('sugar', sugar);
      window.location.search = params.toString();
    });
  });

  document.getElementById('subscription-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('subscription-overlay')) {
      e.target.classList.add('hidden');
    }
  });

  document.getElementById('notification-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('notification-overlay')) {
      e.target.classList.add('hidden');
    }
  });


  document.getElementById('subscription-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const topicSelect = document.getElementById('topic-select');
    const durationUnit = document.getElementById('duration-unit');
    const durationAmount = document.getElementById('duration-amount');
    const mobileNumber = document.getElementById('mobile-number');
    const totalPrice = document.getElementById('total-price');
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
      return;
    }

    const mobileRegex = /^07\d{8}$/;
    if (!mobileRegex.test(mobileNumber.value)) {
      alert('Please enter a valid mobile number (07xxxxxxxx)');
      return;
    }

    const priceText = totalPrice.textContent.replace('UGX ', '').replace(/,/g, '');
    const priceValue = parseFloat(priceText);
    if (isNaN(priceValue)) {
        alert('Invalid price format');
        return;
    } 

    const subscriptionData = {
      topic_id: topicId, 
      user_id: userId,
      duration_unit: durationUnit.value,
      duration_amount: durationValue, 
      mobile_number: mobileNumber.value,
      total_price: priceValue
    };

    submitBtn.disabled = true;

    try {
      const response = await fetch('/subscribe/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(subscriptionData)
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
    }
  });
});
