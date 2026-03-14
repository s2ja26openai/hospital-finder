// static/js/chatbot.js
const MOCK_RESPONSES = {
  default: [
    { name: '내과', reason: '감기, 편두통, 소화기 증상 가능성' },
    { name: '신경과', reason: '두통 관련 신경계 질환 가능성' },
    { name: '이비인후과', reason: '귀, 코, 목 관련 증상 가능성' }
  ],
  열: [
    { name: '내과', reason: '발열, 감기, 독감 가능성' },
    { name: '소아청소년과', reason: '소아 발열의 경우' },
    { name: '감염내과', reason: '고열 지속 시 감염 질환 가능성' }
  ],
  배: [
    { name: '내과', reason: '소화기 질환, 위염, 장염 가능성' },
    { name: '외과', reason: '급성 복통, 맹장염 가능성' },
    { name: '산부인과', reason: '여성의 경우 자궁/난소 관련 가능성' }
  ],
  피부: [
    { name: '피부과', reason: '피부 질환, 습진, 알레르기 가능성' },
    { name: '내과', reason: '전신 질환에 의한 피부 증상 가능성' },
    { name: '성형외과', reason: '상처 관련 치료 필요 시' }
  ]
};

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

function getMockDepts(symptom) {
  for (const [key, depts] of Object.entries(MOCK_RESPONSES)) {
    if (key !== 'default' && symptom.includes(key)) return depts;
  }
  return MOCK_RESPONSES.default;
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

function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  addBubble(text, 'user');
  addTypingIndicator();

  setTimeout(() => {
    removeTypingIndicator();
    addBubble('입력하신 증상을 분석했습니다. 아래 진료과를 추천드려요:', 'bot');
    addDeptCards(getMockDepts(text));
  }, 1200);
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chatInput');
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMessage();
  });

  // URL에서 초기 증상값 처리
  const urlParams = new URLSearchParams(window.location.search);
  const symptom = urlParams.get('symptom');
  if (symptom) {
    input.value = symptom;
    setTimeout(() => sendMessage(), 300);
  }
});
