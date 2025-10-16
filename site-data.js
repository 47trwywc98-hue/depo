async function loadRemoteData() {
    try {
        const response = await fetch('data/doganismakinalari-data.json', { cache: 'no-store' });
        if (!response.ok) {
            throw new Error(`Veri dosyası yüklenemedi: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Veri dosyası okunamadı:', error);
        return null;
    }
}

function updatePhoneLink(elementId, phoneNumber) {
    if (!phoneNumber) {
        return;
    }
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = phoneNumber;
        element.setAttribute('href', `tel:${phoneNumber.replace(/[^+\d]/g, '')}`);
    }
}

function updateEmailLink(elementId, email) {
    if (!email) {
        return;
    }
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = email;
        element.setAttribute('href', `mailto:${email}`);
    }
}

function renderStockItems(machines) {
    const stockContainer = document.getElementById('stock-list');
    const emptyMessage = document.getElementById('stock-empty-message');

    if (!stockContainer) {
        return;
    }

    stockContainer.innerHTML = '';

    if (!Array.isArray(machines) || machines.length === 0) {
        if (emptyMessage) {
            emptyMessage.textContent = 'Stok bilgisi şu anda mevcut değil. Lütfen daha sonra tekrar deneyin.';
            emptyMessage.hidden = false;
        }
        return;
    }

    machines.forEach((machine) => {
        const card = document.createElement('article');
        card.className = 'inventory-card';

        const title = document.createElement('h3');
        title.textContent = machine.title || 'Stok Makinesi';
        card.appendChild(title);

        if (Array.isArray(machine.specs) && machine.specs.length > 0) {
            const list = document.createElement('ul');
            machine.specs.forEach((spec) => {
                const item = document.createElement('li');
                item.textContent = spec;
                list.appendChild(item);
            });
            card.appendChild(list);
        }

        if (machine.detailUrl) {
            const link = document.createElement('a');
            link.className = 'link';
            link.href = machine.detailUrl;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = 'İlanda görüntüle';
            card.appendChild(link);
        }

        stockContainer.appendChild(card);
    });

    if (emptyMessage) {
        emptyMessage.hidden = true;
    }
}

function updateContactInfo(contact) {
    if (!contact) {
        return;
    }

    updatePhoneLink('header-phone', contact.phone);
    updatePhoneLink('service-phone', contact.servicePhone || contact.phone);
    updatePhoneLink('contact-phone', contact.phone);
    updateEmailLink('contact-email', contact.email);

    if (contact.address) {
        const addressElement = document.getElementById('contact-address');
        if (addressElement) {
            addressElement.textContent = contact.address;
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const loadingMessage = document.getElementById('stock-empty-message');
    if (loadingMessage) {
        loadingMessage.textContent = 'Stok bilgisi yükleniyor...';
        loadingMessage.hidden = false;
    }

    const data = await loadRemoteData();
    if (data) {
        renderStockItems(data.machines);
        updateContactInfo(data.contact);
    } else if (loadingMessage) {
        loadingMessage.textContent = 'Stok bilgisi alınamadı. Lütfen bağlantınızı kontrol edin.';
    }
});
