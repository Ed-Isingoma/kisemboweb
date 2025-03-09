
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


  // function getCSRFToken() {
  //   const cookieValue = document.cookie.match(/(^|;)\\s*csrftoken\\s*=\\s*([^;]+)/);
  //   return cookieValue ? cookieValue.pop() : "";
  // }

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

  // Sidebar video selection: add sugar parameter and reload
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

  // Subscriptions Modal trigger
  document.getElementById('subscriptions')?.addEventListener('click', () => {
    document.getElementById('subscriptions-modal').classList.remove('hidden');
  });
});
