// static/js/chatbot.js
let sessionId = '';

function getMessagesContainer() {
  return document.getElementById('chatMessages');
}

function addBubble(text, type) {
  const container = getMessagesContainer();
  const div = document.createElement('div');
  div.className = `bubble bubble-${type}`;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function addTypingIndicator() {
  const container = getMessagesContainer();
  const div = document.createElement('div');
  div.className = 'bubble bubble-bot bubble-typing';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

function addDeptCards(depts) {
  const container = getMessagesContainer();
  const wrapper = document.createElement('div');
  wrapper.className = 'dept-recommendation';

  depts.forEach(dept => {
    const card = document.createElement('div');
    card.className = 'dept-card';
    card.innerHTML = `
      <div>
        <div class="dept-card-name">${dept.name}</div>
        <div class="dept-card-reason">${dept.reason}</div>
      </div>
      <span class="dept-card-arrow">→</span>
    `;
    card.onclick = () => {
      window.location.href = `/hospitals?department=${encodeURIComponent(dept.name)}`;
    };
    wrapper.appendChild(card);
  });

  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  input.disabled = true;
  addBubble(text, 'user');
  addTypingIndicator();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    const data = await res.json();
    sessionId = data.session_id || sessionId;

    removeTypingIndicator();
    addBubble(data.message || '증상을 분석했습니다. 아래 진료과를 추천드려요:', 'bot');
    if (data.departments && data.departments.length > 0) {
      addDeptCards(data.departments);
    }
  } catch (e) {
    removeTypingIndicator();
    addBubble('일시적인 오류가 발생했습니다. 다시 시도해 주세요.', 'bot');
  } finally {
    input.disabled = false;
    input.focus();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chatInput');
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMessage();
  });

  const urlParams = new URLSearchParams(window.location.search);
  const symptom = urlParams.get('symptom');
  if (symptom) {
    input.value = symptom;
    setTimeout(() => sendMessage(), 300);
  }
});
