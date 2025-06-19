// Вывод всплывашки с сообщениями
const onAlert = (text, type='success', time=3000) => {
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
            const resJson = await res.json();
            onAlert(resJson.error || "Ошибка загрузки", "error");
        }
    } catch (err) {
        onAlert("Ошибка сервера", "error");
    }
};

// Генерация списка фотографий
const renderList = (list) => {
    const tbody = document.getElementById("tbody");

    list.forEach((i => {
        const tr = document.createElement("tr");
        const img = document.createElement("img");
        img.src = 'img/img.svg';
        img.alt = 'img';
        const tdName = document.createElement("td");
        tdName.classList.add('td', 'name');
        tdName.append(img, i.original_name);
        tr.appendChild(tdName);
        tbody.appendChild(tr);
        const link = document.createElement("a");
        link.href = `http://localhost/${i.filename}.${i.file_type}`;
        link.target = '_blank';
        link.classList.add('link');
        link.textContent = i.original_name;
        const tdLink = document.createElement("td");
        tdLink.classList.add('td', 'url');
        tdLink.appendChild(link);
        tr.appendChild(tdLink);
        const icon = document.createElement("img");
        icon.src = 'img/delete.svg';
        icon.alt = 'delete';
        const button = document.createElement("button");
        button.classList.add('deleteBtn');
        button.addEventListener("click", () => onDelete(i.id));
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
const onDelete = async (id) => {
    try {
        const res = await fetch('/images', { method: 'DELETE', body: id });

        if (res.ok) {
            await onListUpdate();
            onAlert("Файл успешно удален", "success");
        } else {
            onAlert("Ошибка удаления файла", "error");
        }
    } catch (err) {
        onAlert("Ошибка сервера", "error");
    }
};

window.onload = async function() {
    await onListUpdate();
};