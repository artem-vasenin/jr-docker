const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const dropzoneTitle = document.getElementById('dropzoneTitle');
const getLinkBtn = document.getElementById('getLinkBtn');
const myAlert = document.getElementById('myAlert');
const linkText = document.getElementById('linkText');
const copyLinkBtn = document.getElementById('copyLinkBtn');

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

// Добавляем ссылку на отправленный файл в текстовое поле
getLinkBtn.addEventListener('click', e => {
    const path = e.target.dataset.path;
    if (path) {
        linkText.value = `http://0.0.0.0:8000/${path}`;
        checkCopyBtn();
    }
});

// Копируем ссылку на файл в буфер обмена
copyLinkBtn.addEventListener('click', e => {
    const path = e.target.dataset.path;
    if (path) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(`http://0.0.0.0:8000/${path}`)
            .then(() => {
                onAlert('Path was copied');
            })
            .catch(err => {
                onAlert('Copy is failed', 'error');
            });
        } else {
            // fallback для старых браузеров или не-HTTPS
            const textarea = document.createElement('textarea');
            textarea.value = `http://0.0.0.0:8000/${path}`;
            textarea.style.position = 'fixed';
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();
            try {
              document.execCommand('copy');
              onAlert('Path was copied');
            } catch (err) {
              onAlert('Copy is failed', 'error');
            }
            document.body.removeChild(textarea);
        }
    }
});

// Функция вывода всплывающих сообщений
const onAlert = (text, type='success', time=5000) => {
        myAlert.innerText = text;
        myAlert.classList.add('active', type);
    setTimeout(() => {
        myAlert.innerText = '';
        myAlert.classList.remove('active', type);
    }, time);
};

// Проверка доступности кнопки показа ссылки
const checkLinkBtn = () => {
    const path = getLinkBtn.dataset.path;
    if (!path) {
        getLinkBtn.setAttribute('disabled', 'disabled');
    } else {
        getLinkBtn.removeAttribute('disabled');
    }
};

// Проверка доступности кнопки копирования ссылки
const checkCopyBtn = () => {
    const value = linkText.value;
    if (!value) {
        copyLinkBtn.setAttribute('disabled', 'disabled');
    } else {
        copyLinkBtn.removeAttribute('disabled');
    }
};

// Запускаем проверку доступности кнопок
checkLinkBtn();
checkCopyBtn();

// Отправка файлов на сервер
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
                const resJson = await res.json();
                getLinkBtn.dataset.path = resJson.path;
                copyLinkBtn.dataset.path = resJson.path;
                linkText.value = '';
                checkLinkBtn();
                checkCopyBtn();
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