console.clear();

const loginBtn = document.getElementById('login');
const signupBtn = document.getElementById('signup');

loginBtn.addEventListener('click', (e) => {
	let parent = e.target.parentNode.parentNode;
	Array.from(e.target.parentNode.parentNode.classList).find((element) => {
		if(element !== "slide-up") {
			parent.classList.add('slide-up')
		}else{
			signupBtn.parentNode.classList.add('slide-up')
			parent.classList.remove('slide-up')
		}
	});
});

signupBtn.addEventListener('click', (e) => {
	let parent = e.target.parentNode;
	Array.from(e.target.parentNode.classList).find((element) => {
		if(element !== "slide-up") {
			parent.classList.add('slide-up')
		}else{
			loginBtn.parentNode.parentNode.classList.add('slide-up')
			parent.classList.remove('slide-up')
		}
	});
});

const passwordInput = document.getElementById('passwordInput');
const togglePassword = document.getElementById('togglePassword');

if (passwordInput && togglePassword) {
	togglePassword.addEventListener('click', () => {
		const isPassword = passwordInput.getAttribute('type') === 'password';
		passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
		togglePassword.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
	});
}
