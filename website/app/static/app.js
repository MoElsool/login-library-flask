function showErrors(errors) {
    const box = document.getElementById('clientErrors');
    box.replaceChildren();
    errors.forEach(msg => {
        const d = document.createElement('div');
        d.className = 'error';
        d.textContent = msg;
        box.appendChild(d);
    });
}

function validateTitle(value) {
    if (!value.trim()) return "Title is required";
    if (value.trim().length > 200) return "Title is too long (200 characters at most)";
    return null;
}

const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', e => {
        const f = e.target, errors = [];
        if (!f.elements['email'].value.trim()) errors.push("Email is required");
        if (!f.elements['password'].value) errors.push("Password is required");
        showErrors(errors);
        if (errors.length) e.preventDefault();
    });
}

const regForm = document.getElementById('regForm');
if (regForm) {
    regForm.addEventListener('submit', e => {
        const f = e.target, errors = [];
        const pw = f.elements['password'].value;
        const cpw = f.elements['confirm_password'].value;
        if (!f.elements['name'].value.trim()) errors.push("Name is required");
        const email = f.elements['email'].value.trim();
        if (!email) errors.push("Email is required");
        else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) errors.push("Email format is invalid");
        if (!pw) errors.push("Password is required");
        else if (new TextEncoder().encode(pw).length > 72) errors.push("Password is too long (72 bytes at most)");
        if (!cpw) errors.push("Confirm password is required");
        if (pw && cpw && pw !== cpw) errors.push("Passwords do not match");
        showErrors(errors);
        if (errors.length) e.preventDefault();
    });
}

document.querySelectorAll('form[data-title-form]').forEach(form => {
    form.addEventListener('submit', e => {
        const msg = validateTitle(form.elements['title'].value);
        showErrors(msg ? [msg] : []);
        if (msg) e.preventDefault();
    });
});