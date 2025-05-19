// Вывод всплывашки с сообщениями
const onAlert = (text, type='success', time=5000) => {
        myAlert.innerText = text;
        myAlert.classList.add('active', type);
    setTimeout(() => {
        myAlert.innerText = '';
        myAlert.classList.remove('active', type);
    }, time);
};

// Получение списка фоток от сервера
const fetchList = async () => {
    try {
        const res = await fetch('/get-images');

        if (res.ok) {
            const resJson = await res.json();
            return resJson.list;
        } else {
            onAlert("Upload error", "error", 3000);
        }
    } catch (err) {
        onAlert("Server error", "error", 3000);
    }
};

// Генерация списка фотографий
const renderList = (list) => {
    const tbody = document.getElementById("tbody");

    list.forEach((i => {
        const fileName = i.split('__name__')[1];
        const tr = document.createElement("tr");
        const img = document.createElement("img");
        img.src = 'img/img.svg';
        img.alt = 'img';
        const tdName = document.createElement("td");
        tdName.classList.add('td', 'name');
        tdName.append(img, fileName);
        tr.appendChild(tdName);
        tbody.appendChild(tr);
        const link = document.createElement("a");
        link.href = `http://localhost:8080/${i}`;
        link.target = '_blank';
        link.classList.add('link');
        link.textContent = i;
        const tdLink = document.createElement("td");
        tdLink.classList.add('td', 'url');
        tdLink.appendChild(link);
        tr.appendChild(tdLink);
        const icon = document.createElement("img");
        icon.src = 'img/delete.svg';
        icon.alt = 'delete';
        const button = document.createElement("button");
        button.classList.add('deleteBtn');
        button.addEventListener("click", () => onDelete(i));
        button.appendChild(icon);
        const tdDelete = document.createElement("td");
        tdDelete.classList.add('td', 'delete');
        tdDelete.appendChild(button);
        tr.appendChild(tdDelete);
    }));
};

// Обновление списка фотографий
const onListUpdate = async () => {
    const table = document.getElementById("table");
    const tbody = document.getElementById("tbody");
    const empty = document.getElementById("empty");
    const list = await fetchList();
    tbody.innerText = '';
    if (list.length) {
        renderList(list);
        empty.classList.add('hide');
        table.classList.remove('hide');
    } else {
        empty.classList.remove('hide');
        table.classList.add('hide');
    }
};

// Удаление элемента из списка
const onDelete = async (url) => {
    try {
        const res = await fetch('/images', { method: 'DELETE', body: url });

        if (res.ok) {
            await onListUpdate();
            onAlert("File was deleted", "success", 3000);
        } else {
            onAlert("Delete is incomplete", "error", 3000);
        }
    } catch (err) {
        onAlert("Server error", "error", 3000);
    }
};

window.onload = async function() {
    await onListUpdate();
};