// Auto-detect API base URL based on current host
const API_BASE_URL = window.location.origin + '/api';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const visualizationContainer = document.getElementById('visualizationContainer');
const ticketModal = document.getElementById('ticketModal');
const createTicketBtn = document.getElementById('createTicketBtn');
const ticketForm = document.getElementById('ticketForm');
const closeModal = document.querySelector('.close');

let currentChart = null;

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

createTicketBtn.addEventListener('click', () => {
    ticketModal.style.display = 'block';
});

closeModal.addEventListener('click', () => {
    ticketModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === ticketModal) {
        ticketModal.style.display = 'none';
    }
});

ticketForm.addEventListener('submit', createTicket);

// Functions
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage('user', message);
    messageInput.value = '';

    // Show loading
    const loadingId = addMessage('bot', 'Javob kutilmoqda...', true);

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Remove loading message
        removeMessage(loadingId);

        // Debug logging
        console.log('Response data:', data);

        if (data.error) {
            addMessage('bot', `Xato: ${data.error}`);
            showError(data.error);
        } else {
            // Add bot response
            let botMessage = '';
            if (data.answer) {
                botMessage = data.answer;
            } else if (data.tool_used) {
                botMessage = `Tool ishlatildi: ${data.tool_used}`;
                if (data.explanation) {
                    botMessage += `\n\n${data.explanation}`;
                }
            }
            addMessage('bot', botMessage || 'Javob olingan');

            // Show visualization - prioritize visualization object
            if (data.visualization && data.visualization.type) {
                console.log('Displaying visualization:', data.visualization);
                displayVisualization(data.visualization, data.result);
            } else if (data.result !== undefined && data.result !== null) {
                console.log('Displaying result:', data.result);
                displayResult(data.result, data.tool_used);
            } else {
                console.log('No visualization or result to display');
            }
        }
    } catch (error) {
        removeMessage(loadingId);
        addMessage('bot', `Xato: ${error.message}`);
        showError('Server bilan bog\'lanishda xato');
    }
}

function addMessage(type, content, isLoading = false) {
    const messageDiv = document.createElement('div');
    const id = isLoading ? 'loading-' + Date.now() : null;
    if (id) messageDiv.id = id;
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (type === 'user') {
        contentDiv.innerHTML = `<strong>Siz:</strong> ${escapeHtml(content)}`;
    } else {
        contentDiv.innerHTML = `<strong>Bot:</strong> ${escapeHtml(content)}`;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return id;
}

function removeMessage(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function displayVisualization(visualization, result) {
    if (!visualization || !visualization.type) {
        console.error('Invalid visualization object:', visualization);
        return;
    }

    visualizationContainer.innerHTML = '';

    if (visualization.type === 'stat') {
        const statCard = document.createElement('div');
        statCard.className = 'stat-card';
        const value = result !== undefined ? result : (visualization.value !== undefined ? visualization.value : 'N/A');
        statCard.innerHTML = `
            <div class="stat-label">Jami qatorlar</div>
            <div class="stat-value">${value}</div>
        `;
        visualizationContainer.appendChild(statCard);
    } else if (visualization.type === 'table') {
        if (visualization.data && Array.isArray(visualization.data) && visualization.data.length > 0) {
            const table = createTable(visualization.data, visualization.columns || Object.keys(visualization.data[0]));
            visualizationContainer.appendChild(table);
        } else {
            visualizationContainer.innerHTML = '<div class="placeholder">Ma\'lumot topilmadi</div>';
        }
    } else if (visualization.type === 'chart') {
        const canvas = document.createElement('canvas');
        canvas.id = 'resultChart';
        const chartDiv = document.createElement('div');
        chartDiv.className = 'chart-container';
        chartDiv.appendChild(canvas);
        visualizationContainer.appendChild(chartDiv);
        
        // Destroy previous chart
        if (currentChart) {
            currentChart.destroy();
            currentChart = null;
        }
        
        // Prepare data
        const labels = visualization.labels || [];
        const values = visualization.values || [];
        
        if (labels.length === 0 || values.length === 0) {
            visualizationContainer.innerHTML = '<div class="placeholder">Grafik uchun ma\'lumot yetarli emas</div>';
            return;
        }
        
        try {
            currentChart = new Chart(canvas, {
                type: visualization.chart_type || 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Qiymat',
                        data: values,
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                        ],
                        borderColor: [
                            'rgba(102, 126, 234, 1)',
                            'rgba(118, 75, 162, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.parsed.y.toLocaleString();
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Chart creation error:', error);
            visualizationContainer.innerHTML = '<div class="error-message">Grafik yaratishda xato: ' + error.message + '</div>';
        }
    } else {
        console.warn('Unknown visualization type:', visualization.type);
        visualizationContainer.innerHTML = '<div class="placeholder">Noma\'lum vizualizatsiya turi</div>';
    }
}

function displayResult(result, toolUsed) {
    visualizationContainer.innerHTML = '';

    if (result === null || result === undefined) {
        visualizationContainer.innerHTML = '<div class="placeholder">Ma\'lumot topilmadi</div>';
        return;
    }

    if (typeof result === 'number') {
        const statCard = document.createElement('div');
        statCard.className = 'stat-card';
        statCard.innerHTML = `
            <div class="stat-label">${toolUsed || 'Natija'}</div>
            <div class="stat-value">${result.toLocaleString()}</div>
        `;
        visualizationContainer.appendChild(statCard);
    } else if (Array.isArray(result)) {
        if (result.length > 0) {
            const columns = Object.keys(result[0]);
            const table = createTable(result, columns);
            visualizationContainer.appendChild(table);
        } else {
            visualizationContainer.innerHTML = '<div class="placeholder">Ma\'lumot topilmadi</div>';
        }
    } else if (typeof result === 'object' && result !== null) {
        // Display as key-value pairs or chart
        const keys = Object.keys(result);
        const values = Object.values(result);
        
        if (keys.length === 0) {
            visualizationContainer.innerHTML = '<div class="placeholder">Bo\'sh ma\'lumot</div>';
            return;
        }
        
        if (keys.length <= 4) {
            // Show as stat cards
            keys.forEach((key, index) => {
                const statCard = document.createElement('div');
                statCard.className = 'stat-card';
                statCard.style.marginBottom = '15px';
                const value = values[index];
                statCard.innerHTML = `
                    <div class="stat-label">${key.replace('_', ' ')}</div>
                    <div class="stat-value">${formatValue(value)}</div>
                `;
                visualizationContainer.appendChild(statCard);
            });
        } else {
            // Show as chart
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            const canvas = document.createElement('canvas');
            canvas.id = 'resultChart';
            chartDiv.appendChild(canvas);
            visualizationContainer.appendChild(chartDiv);
            
            if (currentChart) {
                currentChart.destroy();
                currentChart = null;
            }
            
            try {
                currentChart = new Chart(canvas, {
                    type: 'bar',
                    data: {
                        labels: keys,
                        datasets: [{
                            label: 'Qiymat',
                            data: values.map(v => typeof v === 'number' ? v : 0),
                            backgroundColor: 'rgba(102, 126, 234, 0.8)',
                            borderColor: 'rgba(102, 126, 234, 1)',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Chart creation error:', error);
                visualizationContainer.innerHTML = '<div class="error-message">Grafik yaratishda xato</div>';
            }
        }
    } else {
        visualizationContainer.innerHTML = `<div class="placeholder">${result}</div>`;
    }
}

function createTable(data, columns) {
    const table = document.createElement('table');
    table.className = 'data-table';
    
    // Header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col.charAt(0).toUpperCase() + col.slice(1).replace('_', ' ');
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Body
    const tbody = document.createElement('tbody');
    data.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = formatValue(row[col]);
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    
    return table;
}

function formatValue(value) {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
        return value.toLocaleString();
    }
    if (typeof value === 'string' && value.includes('T') && value.includes('Z')) {
        // ISO date string
        return new Date(value).toLocaleString();
    }
    return value;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    visualizationContainer.innerHTML = '';
    visualizationContainer.appendChild(errorDiv);
}

async function createTicket(e) {
    e.preventDefault();
    
    const title = document.getElementById('ticketTitle').value;
    const description = document.getElementById('ticketDescription').value;
    const priority = document.getElementById('ticketPriority').value;
    const integration = document.getElementById('ticketIntegration').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/ticket/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                description,
                priority,
                integrate_with: integration || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Ticket muvaffaqiyatli yaratildi!');
            ticketModal.style.display = 'none';
            ticketForm.reset();
        } else {
            alert('Xato: ' + (data.detail || 'Noma\'lum xato'));
        }
    } catch (error) {
        alert('Xato: ' + error.message);
    }
}

// Load data summary on page load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/data/summary`);
        const data = await response.json();
        
        if (data.summary) {
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'stat-card';
            summaryDiv.innerHTML = `
                <div class="stat-label">Ma'lumotlar bazasi statistikasi</div>
                <div style="margin-top: 20px; text-align: left;">
                    <p>Foydalanuvchilar: ${data.summary.total_users}</p>
                    <p>Buyurtmalar: ${data.summary.total_orders}</p>
                    <p>Savdolar: ${data.summary.total_sales}</p>
                    <p>Jami daromad: $${data.summary.total_revenue.toLocaleString()}</p>
                </div>
            `;
            visualizationContainer.appendChild(summaryDiv);
        }
    } catch (error) {
        console.error('Error loading summary:', error);
    }
});

