const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const dropzoneTitle = document.getElementById('dropzoneTitle');
const myAlert = document.getElementById('myAlert');

// При клике на drop-зону открываем диалог выбора файла
dropzone.addEventListener('click', () => fileInput.click());

// При выборе файла вручную
fileInput.addEventListener('change', (e) => {
  handleFiles(e.target.files);
});

// Drag-and-drop
dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  handleFiles(e.dataTransfer.files);
});

const onAlert = (text, type='success', time=5000) => {
        myAlert.innerText = text;
        myAlert.classList.add('active', type);
    setTimeout(() => {
        myAlert.innerText = '';
        myAlert.classList.remove('active', type);
    }, time);
};

async function handleFiles(files) {
const file = files[0];
  if (file) {
      if (file.size < 5 * 1024 * 1024 && ['image/jpeg', 'image/png', 'image/gif'].includes(file.type)) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/upload', { method: 'POST', body: formData });

            if (res.ok) {
                onAlert("Upload success", "success", 3000);
            } else {
                onAlert("Upload error", "error", 3000);
            }
        } catch (err) {
            onAlert("Server error", "error", 3000);
        }
      } else {
        onAlert('Upload failed', 'error', 3000);
        dropzoneTitle.textContent = "Upload failed";
        dropzoneTitle.style.color = 'red';
        setTimeout(() => {
            dropzoneTitle.textContent = "Select a file or drag and drop here";
            dropzoneTitle.style.color = '#0B0B0B';
        }, 3000);
      }
  }
}