const getUrl = () => {
    const list = ['img/h1.png', 'img/h2.png', 'img/h3.png', 'img/h4.png', 'img/h5.png'];
    return list[Math.floor(Math.random() * list.length)];
};

const renderImg = () => {
    const imageBlock = document.getElementById('imageBlock');
    const img = document.createElement("img");
    img.src = getUrl();
    img.alt = 'img';
    img.classList.add('image');
    imageBlock.appendChild(img);
}

window.onload = async function() {
    renderImg();
};