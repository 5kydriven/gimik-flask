document.addEventListener('DOMContentLoaded', function () {
	const registerForm = document.getElementById('registerForm');
	const modal = document.getElementById('my_modal_1');

	registerForm.addEventListener('submit', function (event) {
		event.preventDefault(); // Prevent default form submission

		const formData = new FormData(registerForm);

		fetch('/register', {
			method: 'POST',
			body: formData,
		})
			.then((response) => response.json())
			.then((data) => {
				alert(data.message || data.error); // Show success or error message
				if (data.message) {
					registerForm.reset(); // Reset the form on success
				}
				modal.close();
			})
			.catch((error) => console.error('Error:', error));
	});
});
