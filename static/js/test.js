function timeAgo(timestamp) {
	const now = new Date();
	const past = new Date(timestamp);
	const secondsPast = (now - past) / 1000;

	if (secondsPast < 60) {
		const seconds = Math.floor(secondsPast);
		return `${seconds} sec${seconds === 1 ? '' : 's'} ago`;
	}
	if (secondsPast < 3600) {
		const minutes = Math.floor(secondsPast / 60);
		return `${minutes} min${minutes === 1 ? '' : 's'} ago`;
	}
	if (secondsPast < 86400) {
		const hours = Math.floor(secondsPast / 3600);
		return `${hours} hr${hours === 1 ? '' : 's'} ago`;
	}
	if (secondsPast < 604800) {
		const days = Math.floor(secondsPast / 86400);
		return `${days} day${days === 1 ? '' : 's'} ago`;
	}
	return past.toLocaleDateString();
}

function updateTimestamps() {
	const elements = document.querySelectorAll('.time-ago');
	elements.forEach((element) => {
		const timestamp = element.getAttribute('data-timestamp');
		const relativeTime = timeAgo(timestamp);
		element.textContent = relativeTime; // Set the text
	});
}

document.addEventListener('DOMContentLoaded', function () {
	const registerForm = document.getElementById('registerForm');
	const loginForm = document.getElementById('loginForm');
	const modal = document.getElementById('my_modal_1');
	const signInModal = document.querySelector('#sign_in_modal');
	const logoutButton = document.querySelector('#sign_out');
	const postButton = document.querySelector('#post_button');
	const postInput = document.querySelector('#post_input');

	registerForm.addEventListener('submit', function (event) {
		event.preventDefault();

		const formData = new FormData(registerForm);

		fetch('/register', {
			method: 'POST',
			body: formData,
		})
			.then((response) => response.json())
			.then((data) => {
				alert(data.message || data.error);
				if (data.message) {
					registerForm.reset();
				}
				modal.close();
			})
			.catch((error) => console.error('Error:', error));
	});

	signInModal.addEventListener('submit', function (event) {
		event.preventDefault();

		const formData = new FormData(loginForm);

		fetch('/login', {
			method: 'POST',
			body: formData,
		})
			.then((response) => response.json())
			.then((data) => {
				alert(data.message || data.error);
				if (data.message) {
					loginForm.reset();
				}
				modal.close();
				window.location.href = '/';
			})
			.catch((error) => console.error('Error:', error));
	});

	document.querySelectorAll('.like-button').forEach((button) => {
		button.addEventListener('click', async () => {
			const postId = button.dataset.postId;
			const isLiked = button.dataset.liked === 'true'; // Convert string to boolean
			const likeCountSpan = button.querySelector('.like-count');

			try {
				const response = await fetch(`/like/${postId}`, { method: 'POST' });
				const data = await response.json();

				if (response.ok) {
					button.dataset.liked = !isLiked; // Toggle state
					likeCountSpan.textContent = data.likes_count;
					window.location.href = '/';
				} else {
					console.error('Error:', data);
				}
			} catch (error) {
				console.error('Error:', error);
			}
		});
	});

	document.querySelectorAll('.delete-button').forEach((button) => {
		button.addEventListener('click', async () => {
			const postId = button.dataset.postId;

			try {
				const response = await fetch(`/posts/${postId}`, { method: 'DELETE' });
				const data = await response.json();

				alert(data.message || data.error);
				window.location.href = '/';
			} catch (error) {
				console.error('Error:', error);
			}
		});
	});

	if (logoutButton) {
		logoutButton.addEventListener('click', async function () {
			const response = await fetch('/logout', { method: 'GET' });
			console.log(response);
			if (response.ok) {
				window.location.href = '/';
			} else {
				alert('Failed to log out. Please try again.');
			}
		});
	}

	if (postButton) {
		postButton.addEventListener('click', function (event) {
			event.preventDefault();

			if (!postInput.value.trim()) {
				alert('Post content cannot be empty!');
				return;
			}

			const formData = new FormData();
			formData.append('content', postInput.value);

			fetch('/posts', {
				method: 'POST',
				body: formData,
			})
				.then((response) => response.json())
				.then((data) => {
					if (data.message) {
						postInput.value = '';
					}
					modal.close();
					window.location.href = '/';
				})
				.catch((error) => console.error('Error:', error));
		});
	}

	updateTimestamps();
});
// Update every minute
setInterval(updateTimestamps, 60000);
