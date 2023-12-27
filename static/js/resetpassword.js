function resetPassword(event) {
    event.preventDefault();
    console.log(event);
    const form = document.getElementById('resetForm');
    const formData = new FormData(form);

    const formDataObject = {};
    formData.forEach((value, key) => {
        formDataObject[key] = value;
    });
    const headers = {
        'Content-Type': 'application/json',
    }
    axios.post('/users/forgot_password/reset', formDataObject, { headers })
        .then(response => {
            alert("Password reset successful");
        })
        .catch(error => {
            console.error("Error:", error);
        })
}
