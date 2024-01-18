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
    axios.post('/users/reset_password', formDataObject, { headers })
        .then(response => {
            alert("Password reset successful");
        })
        .catch(error => {
            alert("Error: " + error.response.data.detail)
        })
}

