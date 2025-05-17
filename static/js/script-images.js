const onAlert = (text, type='success', time=5000) => {
        myAlert.innerText = text;
        myAlert.classList.add('active', type);
    setTimeout(() => {
        myAlert.innerText = '';
        myAlert.classList.remove('active', type);
    }, time);
};

const onDelete = async (url) => {
    try {
        const res = await fetch('/upload', { method: 'DELETE', body: url });

        if (res.ok) {
            onAlert("File was deleted", "success", 3000);
        } else {
            onAlert("Delete is incomplete", "error", 3000);
        }
    } catch (err) {
        onAlert("Server error", "error", 3000);
    }
};