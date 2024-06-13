const dropdowns = document.querySelectorAll('.dropdown');
//Loop through all dropdown elements
dropdowns. forEach(dropdown => {
//Get inner elements from each dropdown
    const select = dropdown.querySelector('.select');
    const caret = dropdown.querySelector('.caret');
    const menu = dropdown.querySelector ('.menu');
    const options = dropdown.querySelectorAll('.menu li');
    const selected = dropdown.querySelector('.selected');
    const signupForm = document.getElementById('signup-form');

    select.addEventListener ('click', () => {
        //Add the clicked select styles to the select element
        select.classList.toggle('select-clicked');
        //Add the rotate styles to the caret element
        caret.classList.toggle('caret-rotate');
        //Add the open styles to the menu element
        menu.classList.toggle('menu-open');
    });

    options.forEach(option => {
        //Add a click event to the option element
        option. addEventListener ('click', () => {
            //Change selected inner text to clicked option inner text
            selected.innerText = option.innerText;
            select.classList.remove('text-fade-in');
            setTimeout(() => {
                selected.classList.remove("text-fade-in");
     }, 300);
            //Add the clicked select styles to the select element
            select.classList.remove('select-clicked');
            //Add the rotate styles to the caret element
            caret.classList.remove('caret-rotate');
            //Add the open styles to the menu element
            menu.classList.remove('menu-open');

            options.forEach(option => {
                option.classList.remove('active');
    });
  });
        window.addEventListener("click", e => {
            const size = dropdown.getBoundingClientRect();
            if (
                e.clientX < size.left ||
                e.clientX > size.right ||
                e.clientY < size.top ||
                e.clientY > size.bottom
    ) {
                select.classList.remove('select-clicked');
                caret.classList.remove('caret-rotate');
                menu.classList.remove('menu-open');
    }
});

        signupForm.addEventListener('submit', function(event) {
            event.preventDefault();

            // Client-side validation (example: check if all fields are filled)
            const requiredFields = signupForm.querySelectorAll('[required]');
            for (let field of requiredFields) {
                if (!field.value) {
                    alert('Please fill all required fields.');
                    return;
        }
    }

            const formData = new FormData(signupForm);
            fetch('/signup', {
                method: 'POST',
                body: formData
    })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/dashboard';
                } else {
                    alert(data.message);
        }
    })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    });
});



